from ipware import get_client_ip


def browser_version(request):
    return 'Browser: {} version: {}'.format(
        request.user_agent.browser.family,
        request.user_agent.browser.version_string or 'Other'
    )


def os_version(request):
    return 'OS: %s' % request.user_agent.os.family


def ip_address(request):
    return 'IP: %s' % get_client_ip(request)[0]
