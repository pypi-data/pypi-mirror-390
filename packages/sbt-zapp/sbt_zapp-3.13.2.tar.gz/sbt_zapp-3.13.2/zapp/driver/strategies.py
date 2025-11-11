import logging
import threading
from abc import ABC
from time import sleep

import allure

from zapp.driver import BROWSER, DRIVER_IMPL
from zapp.driver.selenium.factory import SeleniumBrowserFactory
from zapp.driver.playwright.factory import PlaywrightBrowserFactory

from zapp.driver import (
    BROWSER_HEIGHT,
    BROWSER_WIDTH,
    BROWSER_LIFECYCLE,
    BROWSER_GO_TO_HOST_ON_START,
    BROWSER_DISABLE_FOR_TAGS,
    REMOTE_BROWSER_PING_ENABLED,
    REMOTE_BROWSER_PING_TIMEOUT_IN_SEC,
    REMOTE_EXECUTOR,
)

log = logging.getLogger("browser_lifecycle")


class BrowserLifecycle(ABC):
    __lock = threading.Lock()

    def before_all(self, context):
        self._start_ping_thread(context)
        self.browser_factory = {
            "SELENIUM": SeleniumBrowserFactory,
            "PLAYWRIGHT": PlaywrightBrowserFactory,
        }[DRIVER_IMPL](context, BROWSER)
        self.disabled_for = set(BROWSER_DISABLE_FOR_TAGS.split(","))

    def is_playwright(self):
        return DRIVER_IMPL == "PLAYWRIGHT"

    def is_selenium(self):
        return DRIVER_IMPL == "SELENIUM"

    def before_feature(self, context):
        pass

    def before_scenario(self, context):
        pass

    def after_scenario(self, context):
        pass

    def after_feature(self, context):
        pass

    def after_all(self, context):
        pass

    def is_browser_created(self, context) -> bool:
        return hasattr(context, "browser")

    def reset_certificates(self, context):
        if hasattr(context, "cert_for_urls"):
            del context.cert_for_urls

    def on_fail(self, context):
        if self.is_browser_created(context):
            allure.attach(
                context.browser.screenshot(),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )

            allure.attach(
                context.browser.page_source(),
                name="page-source",
                attachment_type=allure.attachment_type.HTML,
            )

    def restart(self, context):
        log.info("Перезапускаем браузер...")
        self._stop(context)
        self.start(context)

    def start(self, context):
        if self.is_browser_created(context):
            log.warning("Браузер уже запущен!")
            return

        if hasattr(context, "tags") and self.disabled_for & set(context.tags):
            log.info(
                "Браузер запущен не будет: сценарий содержит один из тегов %s",
                self.disabled_for,
            )
            return

        self._register_cleanup(context)

        log.info("Запуск браузера...")
        log.debug(f"Download directory: {self.browser_factory.download_dir}")

        context.browser = self.browser_factory.create()

        if BROWSER_WIDTH and BROWSER_HEIGHT:
            context.browser.set_window_size(BROWSER_WIDTH, BROWSER_HEIGHT)
        if BROWSER_GO_TO_HOST_ON_START:
            context.browser.open(context.host)

    def _stop(self, context):
        with self.__lock:
            if self.is_browser_created(context):
                log.info("Завершение работы браузера...")
                context.browser.quit()
                delattr(context, "browser")

    def _register_cleanup(self, context):
        """Регистрируем cleanup вместо использования хука after:
        Отработает самым последним (после пользовательских): LIFO
        См. https://github.com/behave/behave/blob/main/features/runner.context_cleanup.feature
        """
        context.add_cleanup(self._stop, context)

    def _start_ping_thread(self, context):
        if REMOTE_EXECUTOR and REMOTE_BROWSER_PING_ENABLED:
            ping_thread = threading.Thread(
                target=self.__ping_driver, args=(context,), daemon=True
            )
            ping_thread.start()
            log.info(
                f"Запущен deamon-поток для опроса Selenoid Session раз в {REMOTE_BROWSER_PING_TIMEOUT_IN_SEC} секунд"
            )

    def __ping_driver(self, context):
        while True:
            with self.__lock:
                if self.is_browser_created(context):
                    try:
                        log.debug("[Deamon] Ping driver...")
                        _ = context.browser.title()
                    except Exception as ex:
                        log.error("[Deamon] Ping driver error: " + str(ex))
            sleep(REMOTE_BROWSER_PING_TIMEOUT_IN_SEC.total_seconds())


class EachScenarioBrowserLifecycle(BrowserLifecycle):

    def before_scenario(self, context):
        self.start(context)

    def after_scenario(self, context):
        self.reset_certificates(context)


class EachFeatureBrowserLifecycle(BrowserLifecycle):

    def before_feature(self, context):
        self.start(context)

    def after_feature(self, context):
        self.reset_certificates(context)


class OneInstanceBrowserLifecycle(BrowserLifecycle):

    def before_all(self, context):
        super().before_all(context)
        self.start(context)

    def after_all(self, context):
        self.reset_certificates(context)


class ManualBrowserLifecycle(BrowserLifecycle):
    pass


browser_lifecycle: BrowserLifecycle = {
    "ONE_INSTANCE": OneInstanceBrowserLifecycle,
    "EACH_FEATURE": EachFeatureBrowserLifecycle,
    "EACH_SCENARIO": EachScenarioBrowserLifecycle,
    "MANUAL": ManualBrowserLifecycle,
}[BROWSER_LIFECYCLE]()
