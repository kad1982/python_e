import logging

from app.core.calendar.repositories import CalendarRepository
from app.core.calendar.services import CalendarService
from telegram.ext import Application as PTBApplication, ApplicationBuilder

from app.core.users.repositories import UserRepository
from app.core.users.services import UserService
from app.handlers import HANDLERS
from app.infra.postgres.base import Base
from app.infra.postgres.db import Database
from settings.config import AppSettings, settings

from app.core.stats.repositories import StatsRepository
from app.core.stats.services import StatsService


class Application(PTBApplication):
    def __init__(self, app_settings: AppSettings, **kwargs):
        super().__init__(**kwargs)
        self._settings = app_settings
        self.database = Database(app_settings.POSTGRES_DSN, declarative_base=Base)

        stats_repository = StatsRepository(database=self.database)
        self.stats_service = StatsService(repository=stats_repository)

        user_repository = UserRepository(database=self.database)
        self.user_service = UserService(repository=user_repository, stats_service=self.stats_service)

        calendar_repository = CalendarRepository(database=self.database)
        self.calendar_service = CalendarService(repository=calendar_repository, stats_service=self.stats_service)





    @staticmethod
    async def application_startup(application: "Application") -> None:
        await application.database.create_tables()
        application.register_handlers()

    @staticmethod
    async def application_shutdown(application: "Application") -> None:
        await application.database.shutdown()

    def run(self) -> None:
        self.run_polling()

    def register_handlers(self) -> None:
        for handler in HANDLERS:
            self.add_handler(handler.handler)


def configure_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


def create_app(app_settings: AppSettings) -> Application:
    application = (ApplicationBuilder()
                   .application_class(Application, kwargs={"app_settings": app_settings})
                   # .arbitrary_callback_data(True)
                   .post_init(Application.application_startup).  # type: ignore[arg-type]
                   post_shutdown(Application.application_shutdown)  # type: ignore[arg-type]
                   .token(app_settings.TELEGRAM_API_KEY.get_secret_value()).build())
    return application  # type: ignore[return-value]


if __name__ == '__main__':
    configure_logging()
    app = create_app(settings)
    app.run()
