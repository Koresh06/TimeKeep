from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class DbConfig:
    password: str
    user: str
    database: str
    host: str
    port: int = 5432

    test_database: Optional[str] = None

    def construct_sqlalchemy_url(self, driver="asyncpg", host=None, port=None, is_test=False) -> str:
        from sqlalchemy.engine.url import URL

        if not host:
            host = self.host
        if not port:
            port = self.port
        
        database = "test_db" if is_test else self.database

        uri = URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password,
            host=host,
            port=port,
            database=database, 
        )
        return uri.render_as_string(hide_password=False)

    @staticmethod
    def from_env(env: Env, is_test=False):
        host = env.str("DB_HOST")
        user = env.str("POSTGRES_USER")
        password = env.str("POSTGRES_PASSWORD")
        database = env.str("POSTGRES_DB")
        port = env.int("DB_PORT", 5432)
        
        test_database = env.str("TEST_POSTGRES_DB")

        if is_test:
            return DbConfig(
                host=host, 
                password=password, 
                user=user, 
                database=database, 
                port=port,
                test_database=test_database
            )

        return DbConfig(
            host=host, 
            password=password, 
            user=user, 
            database=database, 
            port=port,
            test_database=test_database
        )



@dataclass
class ApiConfig:
    """ 
    Creates the ApiConfig object from environment variables.
    """

    secret_key: str
    access_token_expire_minutes: int
    host: str = "127.0.0.1"
    port: int = 8000

    @staticmethod
    def from_env(env: Env):
        """
        Creates the ApiConfig object from environment variables.
        """
        secret_key = env.str("SECRET_KEY")
        access_token_expire_minutes = env.int("ACCESS_TOKEN_EXPIRE_MINUTES")
        host = env.str("API_HOST")
        port = env.int("API_PORT")
        return ApiConfig(
            secret_key=secret_key,
            access_token_expire_minutes=access_token_expire_minutes,
            host=host,
            port=port,
        )


@dataclass
class Settings:
    """
    The main configuration class that integrates all the other configuration classes.

    This class holds the other configuration classes, providing a centralized point of access for all settings.

    Attributes
    ----------
    tg_bot : TgBot
        Holds the settings related to the Telegram Bot.
    db : Optional[DbConfig]
        Holds the settings specific to the database (default is None).
    redis : Optional[RedisConfig]
        Holds the settings specific to Redis (default is None).
    """

    db: Optional[DbConfig] = None
    api: Optional[ApiConfig] = None


def load_settings(path: str) -> Settings:
    """
    This function takes an optional file path as input and returns a Settings object.
    :param path: The path of env file from where to load the configuration variables.
    It reads environment variables from a .env file if provided, else from the process environment.
    :return: Settings object with attributes set as per environment variables.
    """

    env = Env()
    env.read_env(path)

    return Settings(
        db=DbConfig.from_env(env),
        api=ApiConfig.from_env(env),
    )


settings = load_settings(".env")
