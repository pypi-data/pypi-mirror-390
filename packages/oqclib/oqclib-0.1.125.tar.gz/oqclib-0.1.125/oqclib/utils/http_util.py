import requests
import logging

logger = logging.getLogger(__name__)


def send_post_request_with_retries(url, data, headers=None, retries=3, **kwargs):
    # Todo: POST Response: 200 {"code":11232,"data":{},"msg":"frequency limited psm[lark.oapi.app_platform_runtime]appID[1500]"}

    for i in range(retries + 1):
        try:
            response = requests.post(url, data=data, headers=headers, **kwargs)
            logger.info("POST Response: {} {}".format(response.status_code, response.content.decode("utf-8")))
            response.raise_for_status()
            if response.status_code // 100 == 2:
                return response
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            logger.info(f"Retry {i + 1}: {e}")

    return None  # No successful response after retries
