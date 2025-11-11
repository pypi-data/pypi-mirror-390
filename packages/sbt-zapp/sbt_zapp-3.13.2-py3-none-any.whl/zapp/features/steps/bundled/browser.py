from allure import step as allure_step
from logging import getLogger
from behave import step
from urllib.parse import urlparse
from envparse import env

from zapp.driver import CertificateForUrl, PemCertificateData
from zapp.driver.strategies import browser_lifecycle
from zapp.features.steps.bundled.ui import go_to_url, assert_page_load
from zapp.features.core.utils import variables

log = getLogger(__name__)

COOKIE_SET_MAX_ATTEMPTS = env.int("COOKIE_SET_MAX_ATTEMPTS", default=3)

_browser_cookie_fields = {
    # Проставляются все поля, кроме домена,
    # так как мы выставляем только для определенного домена значения (по умолчанию его и берет) +
    # Автоматом криво ставит точку сам клиент перед доменом:
    # https://stackoverflow.com/questions/1062963/how-do-browser-cookie-domains-work/1063760#1063760
    "name": lambda cookie: cookie.name,
    "value": lambda cookie: cookie.value,
    "path": lambda cookie: cookie.path,
    "secure": lambda cookie: cookie.secure,
    "httpOnly": lambda cookie: cookie._rest.get("HttpOnly"),
    "sameSite": lambda cookie: cookie._rest.get("SameSite"),
    "expiry": lambda cookie: cookie.expires,
}

if browser_lifecycle.is_playwright():
    _browser_cookie_fields["domain"] = (
        lambda cookie: cookie.domain
    )  # необходим для Playwright, но наоборот не нужен для Selenium


class MaxAttemptsExceededException(AssertionError):
    pass


def calculate_url_if_needed(context, url):
    if not url:
        parsed_url = urlparse(context.host)
        url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return url


def init_cert_for_urls_attr_if_needed(context):
    if not hasattr(context, "cert_for_urls"):
        context.cert_for_urls = []


def update_cert_for_urls(context, cert_for_url: CertificateForUrl):
    url = cert_for_url.url
    context.cert_for_urls[:] = [
        cert for cert in context.cert_for_urls if cert.url != url
    ]
    context.cert_for_urls.append(cert_for_url)


def configure_client_cert_filter(context, url: str, filter: dict):
    """Selenium. Сертификат должен быть установлен в хранилище сертов ОС"""
    url = calculate_url_if_needed(context, url)
    init_cert_for_urls_attr_if_needed(context)

    update_cert_for_urls(context, CertificateForUrl(url=url, filter=filter))


@step(
    'Я задал для главной страницы клиентский сертификат "{cert_path}" '
    'c приватным ключом "{key_path}"'
)
@step(
    'Я задал для главной страницы клиентский сертификат "{cert_path}" '
    'c приватным ключом "{key_path}" '
    'и passphrase "{passphrase}"'
)
@step(
    'Я задал для главной страницы клиентский сертификат "{cert_path}" '
    'c приватным ключом "{key_path}" '
    'и passphrase из переменной "{passphrase_var}"'
)
@step(
    'Я задал для URL "{url}" клиентский сертификат "{cert_path}" '
    'c приватным ключом "{key_path}"'
)
@step(
    'Я задал для URL "{url}" клиентский сертификат "{cert_path}" '
    'c приватным ключом "{key_path}" '
    'и passphrase "{passphrase}"'
)
@step(
    'Я задал для URL "{url}" клиентский сертификат "{cert_path}" '
    'c приватным ключом "{key_path}" '
    'и passphrase из переменной "{passphrase_var}"'
)
def configure_client_cert_file(
    context,
    cert_path: str,
    key_path: str,
    url: str = None,
    passphrase: str = None,
    passphrase_var: str = None,
):
    """Playwright. Формат сертификата должен быть pem"""
    url = calculate_url_if_needed(context, url)

    init_cert_for_urls_attr_if_needed(context)

    passphrase = passphrase or variables[passphrase_var]

    update_cert_for_urls(
        context,
        CertificateForUrl(
            url=url,
            data=PemCertificateData(
                cert_path=cert_path, key_path=key_path, passphrase=passphrase
            ),
        ),
    )


@step(
    'Я задал для главной страницы клиентский сертификат из переменной "{cert_var}" '
    'c приватным ключом из переменной "{key_var}"'
)
@step(
    'Я задал для главной страницы клиентский сертификат из переменной "{cert_var}" '
    'c приватным ключом из переменной "{key_var}" '
    'и passphrase из переменной "{passphrase_var}"'
)
@step(
    'Я задал для URL "{url}" клиентский сертификат из переменной "{cert_var}" '
    'c приватным ключом из переменной "{key_var}"'
)
@step(
    'Я задал для URL "{url}" клиентский сертификат из переменной "{cert_var}" '
    'c приватным ключом из переменной "{key_var}" '
    'и passphrase из переменной "{passphrase_var}"'
)
def configure_client_cert_content(
    context,
    cert_var: str,
    key_var: str,
    url: str = None,
    passphrase_var: str = None,
):
    """Playwright. Формат сертификата должен быть pem. Строковое значение"""
    url = calculate_url_if_needed(context, url)

    init_cert_for_urls_attr_if_needed(context)

    cert = variables[cert_var].encode()
    key = variables[key_var].encode()
    passphrase = variables[passphrase_var]

    update_cert_for_urls(
        context,
        CertificateForUrl(
            url=url,
            data=PemCertificateData(cert=cert, key=key, passphrase=passphrase),
        ),
    )


@step('Я задал для главной страницы сертификат с CN="{subject_cn}"')
@step('Я задал для URL "{url}" сертификат с CN="{subject_cn}"')
def configure_client_cert_filter_by_subject_cn(
    context, subject_cn: str, url: str = None
):
    configure_client_cert_filter(context, url, {"SUBJECT": {"CN": subject_cn}})


@step('Я задал для главной страницы сертификат с email="{subject_email}"')
@step('Я задал для URL "{url}" сертификат с email="{subject_email}"')
def configure_client_cert_filter_by_subject_email(
    context, subject_email: str, url: str = None
):
    configure_client_cert_filter(
        context, url, {"SUBJECT": {"emailAddress": subject_email}}
    )


@step("Я сбросил конфигурацию сертификатов")
def reset_client_certs(context):
    browser_lifecycle.reset_certificates(context)


@step("Я перезапустил браузер")
def restart_browser(context):
    browser_lifecycle.restart(context)


@step("Я запустил браузер")
def start_browser(context):
    browser_lifecycle.start(context)


@step("Я открыл главную страницу авторизованным")
def open_main_page_by_authorized_user(context):
    host = context.host

    if not hasattr(context, "keycloak_session"):
        raise AssertionError(
            "Не выполнена авторизация по API. Шаг: 'API: Я авторизовался через KeyCloak...'"
        )

    session = context.keycloak_session

    go_to_url(context, host)
    context.browser.wait_for_loading()

    add_cookies_and_refresh(context, session)

    go_to_url(context, host)
    assert_page_load(context)


@step("Я включил запись логов консоли браузера")
def start_console_log_recording(context):
    context.browser.start_console_log_recording()


@step("Я остановил запись логов консоли браузера и сохранил результат")
def stop_console_log_recording(context):
    context.browser_logs = context.browser.stop_console_log_recording()


@allure_step("Установка cookies в браузере")
def add_cookies_and_refresh(context, session):
    previous = None
    try_count = 0

    while True:
        if try_count > COOKIE_SET_MAX_ATTEMPTS:
            raise MaxAttemptsExceededException(
                "Превышено количество попыток установить куки"
            )

        try_count += 1

        # Устанавливаем куки только для открытого в данный момент домена
        domain, cookies = session.domain_cookies(context.browser.url())
        if previous == domain:
            return
        previous = domain

        with allure_step(f"Установка cookie для домена {domain}"):
            log.info(f"Домен: {domain}")
            for cookie in cookies:
                log.info(f"Добавляем cookie: {cookie.name}")
                browser_cookie = {}
                for key, value in _browser_cookie_fields.items():
                    field_value = value(cookie)
                    if field_value is not None:
                        browser_cookie[key] = field_value
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#cookie_prefixes
                if cookie.name.startswith("__Host-"):
                    browser_cookie["sameSite"] = "Strict"
                context.browser.add_cookies([browser_cookie])
            context.browser.refresh()
            context.browser.wait_for_loading()
