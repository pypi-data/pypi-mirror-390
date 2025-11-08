import typing
import aiohttp

if typing.TYPE_CHECKING:
    from _ServiceLib.logger import LoggerType


async def call_lambda(
    lambda_url: str,
    payload: dict,
    logger: "LoggerType" = None
):
    """
    Generic Lambda POST request
    """

    func_trace = "[awsLambdaClient]: {msg}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(lambda_url, json=payload, timeout=5) as resp:
                try:
                    data = await resp.json()
                except Exception:
                    text = await resp.text()
                    if logger:
                        logger.error(
                            f"{func_trace}: Couldn't connect to AWS Lambda\n"
                            f"Response headers: {resp.headers}\n"
                            f"Response payload: {text}"
                        )
                    return None

                if resp.status != 200:
                    if logger:
                        logger.info(func_trace.format(f"External Server Error. '\nReason: {resp.status}"))
                    return None

                if logger:
                    logger.info(func_trace.format(f"Recieved: data of len {len(data)}"))
                return data

    except Exception as e:
        logger.error(f"{func_trace} Internal Error during Lambda call: {str(e)}")
        return None
