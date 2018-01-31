from aiohttp import web

from datacatalog import application


def main() -> int:
    aio_app = application.Application()
    web.run_app(aio_app, port=aio_app.config['web']['port'])
    return 0


if __name__ == '__main__':
    main()