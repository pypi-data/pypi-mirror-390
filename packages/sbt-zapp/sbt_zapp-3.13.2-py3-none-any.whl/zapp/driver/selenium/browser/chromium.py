from abc import abstractmethod
from json import dumps
from typing import Type

from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.chromium.webdriver import ChromiumDriver

from zapp.driver.selenium.browser.base import Browser
from zapp.driver import (
    BROWSER_BINARY_LOCATION,
    BROWSER_HEADLESS,
    BROWSER_LOCALE,
    BROWSER_ENABLE_DARK_COLOR_SCHEME,
    BROWSER_USERAGENT,
    CHROMIUM_DEFAULT_ARGS,
)


class ChromiumBrowser(Browser):

    def _options(self) -> ChromiumOptions:
        # @see https://peter.sh/experiments/chromium-command-line-switches/
        arguments = CHROMIUM_DEFAULT_ARGS.copy()

        if BROWSER_USERAGENT:
            arguments.append(f'--user-agent="{BROWSER_USERAGENT}"')

        if BROWSER_ENABLE_DARK_COLOR_SCHEME:
            arguments.append("--force-dark-mode")

        if BROWSER_HEADLESS:
            arguments.append("--headless=new")

        options = self._options_cls()()

        for arg in set(arguments):
            options.add_argument(arg)

        # @see https://chromium.googlesource.com/chromium/src/+/refs/heads/main/chrome/common/pref_names.h
        # @see https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/content_settings/core/common/pref_names.h
        # @see https://developer.chrome.com/docs/extensions/reference/api/contentSettings
        # 0 - Default, 1 - Allow, 2 - Block, 3 - Ask
        prefs = {
            "profile": {
                "managed_default_content_settings": {
                    "notifications": 2,
                    "popups": 2,
                    "clipboard": 1,
                    "automatic_downloads": 1,
                    "geolocation": 1,
                }
            },
            "download": {
                "prompt_for_download": False,
                "directory_upgrade": True,
                "default_directory": self._download_dir,
            },
            "intl": {"accept_languages": BROWSER_LOCALE},
        }

        if self._cert_for_urls:
            auto_select_config = prefs["profile"][
                "managed_auto_select_certificate_for_urls"
            ] = []
            for cert_for_url in self._cert_for_urls:
                auto_select_config.append(
                    dumps(
                        {
                            "pattern": cert_for_url.url,
                            "filter": cert_for_url.filter,
                        }
                    )
                )

        options.add_experimental_option("prefs", prefs)

        options.set_capability(
            f"{self.options_prefix}:loggingPrefs", {"browser": "ALL"}
        )

        if BROWSER_BINARY_LOCATION:
            options.binary_location = BROWSER_BINARY_LOCATION

        return options

    @abstractmethod
    def _options_cls(self) -> Type[ChromiumOptions]:
        pass

    @abstractmethod
    def _init_driver(self, options) -> ChromiumDriver:
        pass
