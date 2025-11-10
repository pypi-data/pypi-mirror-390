from enum import Enum


class FileLoadBeginColumns(Enum):
    EVENT_CLASS = 0  # Event Class is used to categorize events.
    CURRENT_TIME = 2  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    START_TIME = 3  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    JOB_ID = 7  # Job ID for progress.
    SESSION_TYPE = 8  # Session type (what entity caused the operation).
    OBJECT_ID = 11  # Object ID (note this is a string).
    OBJECT_TYPE = 12  # Object type.
    OBJECT_NAME = 13  # Object name.
    OBJECT_PATH = 14  # Object path. A comma-separated list of parents, starting with the object's parent.
    CONNECTION_ID = 25  # Unique connection ID.
    DATABASE_NAME = 28  # Name of the database in which the statement of the user is running.
    CLIENT_PROCESS_ID = 36  # The process ID of the client application.
    SESSION_ID = 39  # Session GUID.
    TEXT_DATA = 42  # Text data associated with the event.
    SERVER_NAME = 43  # Name of the server producing the event.
    ACTIVITY_ID = 46
    REQUEST_ID = 47


class FileLoadEndColumns(Enum):
    EVENT_CLASS = 0  # Event Class is used to categorize events.
    CURRENT_TIME = 2  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    START_TIME = 3  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    END_TIME = 4  # Time at which the event ended. This column is not populated for starting event classes, such as SQL:BatchStarting or SP:Starting. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    DURATION = 5  # Amount of time (in milliseconds) taken by the event.
    JOB_ID = 7  # Job ID for progress.
    SESSION_TYPE = 8  # Session type (what entity caused the operation).
    INTEGER_DATA = 10  # Integer data.
    OBJECT_ID = 11  # Object ID (note this is a string).
    OBJECT_TYPE = 12  # Object type.
    OBJECT_NAME = 13  # Object name.
    OBJECT_PATH = 14  # Object path. A comma-separated list of parents, starting with the object's parent.
    SEVERITY = 22  # Severity level of an exception.
    SUCCESS = 23  # 1 = success. 0 = failure (for example, a 1 means success of a permissions check and a 0 means a failure of that check).
    ERROR = 24  # Error number of a given event.
    CONNECTION_ID = 25  # Unique connection ID.
    DATABASE_NAME = 28  # Name of the database in which the statement of the user is running.
    CLIENT_PROCESS_ID = 36  # The process ID of the client application.
    SESSION_ID = 39  # Session GUID.
    TEXT_DATA = 42  # Text data associated with the event.
    SERVER_NAME = 43  # Name of the server producing the event.
    ACTIVITY_ID = 46
    REQUEST_ID = 47


class FileSaveBeginColumns(Enum):
    EVENT_CLASS = 0  # Event Class is used to categorize events.
    CURRENT_TIME = 2  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    START_TIME = 3  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    JOB_ID = 7  # Job ID for progress.
    SESSION_TYPE = 8  # Session type (what entity caused the operation).
    OBJECT_ID = 11  # Object ID (note this is a string).
    OBJECT_TYPE = 12  # Object type.
    OBJECT_NAME = 13  # Object name.
    OBJECT_PATH = 14  # Object path. A comma-separated list of parents, starting with the object's parent.
    CONNECTION_ID = 25  # Unique connection ID.
    DATABASE_NAME = 28  # Name of the database in which the statement of the user is running.
    CLIENT_PROCESS_ID = 36  # The process ID of the client application.
    SESSION_ID = 39  # Session GUID.
    TEXT_DATA = 42  # Text data associated with the event.
    SERVER_NAME = 43  # Name of the server producing the event
    ACTIVITY_ID = 46
    REQUEST_ID = 47


class FileSaveEndColumns(Enum):
    EVENT_CLASS = 0  # Event Class is used to categorize events.
    CURRENT_TIME = 2  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    START_TIME = 3  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    END_TIME = 4  # Time at which the event ended. This column is not populated for starting event classes, such as SQL:BatchStarting or SP:Starting. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    DURATION = 5  # Amount of time (in milliseconds) taken by the event.
    JOB_ID = 7  # Job ID for progress.
    SESSION_TYPE = 8  # Session type (what entity caused the operation).
    INTEGER_DATA = 10  # Integer data.
    OBJECT_ID = 11  # Object ID (note this is a string).
    OBJECT_TYPE = 12  # Object type.
    OBJECT_NAME = 13  # Object name.
    OBJECT_PATH = 14  # Object path. A comma-separated list of parents, starting with the object's parent.
    SEVERITY = 22  # Severity level of an exception.
    SUCCESS = 23  # 1 = success. 0 = failure (for example, a 1 means success of a permissions check and a 0 means a failure of that check).
    ERROR = 24  # Error number of a given event.
    CONNECTION_ID = 25  # Unique connection ID.
    DATABASE_NAME = 28  # Name of the database in which the statement of the user is running.
    CLIENT_PROCESS_ID = 36  # The process ID of the client application.
    SESSION_ID = 39  # Session GUID.
    TEXT_DATA = 42  # Text data associated with the event.
    SERVER_NAME = 43  # Name of the server producing the event.
    ACTIVITY_ID = 46
    REQUEST_ID = 47


class PageOutBeginColumns(Enum):
    EVENT_CLASS = 0  # Event Class is used to categorize events.
    CURRENT_TIME = 2  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    START_TIME = 3  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    JOB_ID = 7  # Job ID for progress.
    SESSION_TYPE = 8  # Session type (what entity caused the operation).
    OBJECT_ID = 11  # Object ID (note this is a string).
    OBJECT_TYPE = 12  # Object type.
    OBJECT_NAME = 13  # Object name.
    OBJECT_PATH = 14  # Object path. A comma-separated list of parents, starting with the object's parent.
    CONNECTION_ID = 25  # Unique connection ID.
    DATABASE_NAME = 28  # Name of the database in which the statement of the user is running.
    CLIENT_PROCESS_ID = 36  # The process ID of the client application.
    SESSION_ID = 39  # Session GUID.
    TEXT_DATA = 42  # Text data associated with the event.
    SERVER_NAME = 43  # Name of the server producing the event.
    ACTIVITY_ID = 46
    REQUEST_ID = 47


class PageOutEndColumns(Enum):
    EVENT_CLASS = 0  # Event Class is used to categorize events.
    CURRENT_TIME = 2  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    START_TIME = 3  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    END_TIME = 4  # Time at which the event ended. This column is not populated for starting event classes, such as SQL:BatchStarting or SP:Starting. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    DURATION = 5  # Amount of time (in milliseconds) taken by the event.
    JOB_ID = 7  # Job ID for progress.
    SESSION_TYPE = 8  # Session type (what entity caused the operation).
    INTEGER_DATA = 10  # Integer data.
    OBJECT_ID = 11  # Object ID (note this is a string).
    OBJECT_TYPE = 12  # Object type.
    OBJECT_NAME = 13  # Object name.
    OBJECT_PATH = 14  # Object path. A comma-separated list of parents, starting with the object's parent.
    SEVERITY = 22  # Severity level of an exception.
    SUCCESS = 23  # 1 = success. 0 = failure (for example, a 1 means success of a permissions check and a 0 means a failure of that check).
    ERROR = 24  # Error number of a given event.
    CONNECTION_ID = 25  # Unique connection ID.
    DATABASE_NAME = 28  # Name of the database in which the statement of the user is running.
    CLIENT_PROCESS_ID = 36  # The process ID of the client application.
    SESSION_ID = 39  # Session GUID.
    TEXT_DATA = 42  # Text data associated with the event.
    SERVER_NAME = 43  # Name of the server producing the event.
    ACTIVITY_ID = 46
    REQUEST_ID = 47


class PageInBeginColumns(Enum):
    EVENT_CLASS = 0  # Event Class is used to categorize events.
    CURRENT_TIME = 2  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    START_TIME = 3  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    JOB_ID = 7  # Job ID for progress.
    SESSION_TYPE = 8  # Session type (what entity caused the operation).
    OBJECT_ID = 11  # Object ID (note this is a string).
    OBJECT_TYPE = 12  # Object type.
    OBJECT_NAME = 13  # Object name.
    OBJECT_PATH = 14  # Object path. A comma-separated list of parents, starting with the object's parent.
    CONNECTION_ID = 25  # Unique connection ID.
    DATABASE_NAME = 28  # Name of the database in which the statement of the user is running.
    CLIENT_PROCESS_ID = 36  # The process ID of the client application.
    SESSION_ID = 39  # Session GUID.
    TEXT_DATA = 42  # Text data associated with the event.
    SERVER_NAME = 43  # Name of the server producing the event.
    ACTIVITY_ID = 46
    REQUEST_ID = 47


class PageInEndColumns(Enum):
    EVENT_CLASS = 0  # Event Class is used to categorize events.
    CURRENT_TIME = 2  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    START_TIME = 3  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    END_TIME = 4  # Time at which the event ended. This column is not populated for starting event classes, such as SQL:BatchStarting or SP:Starting. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    DURATION = 5  # Amount of time (in milliseconds) taken by the event.
    JOB_ID = 7  # Job ID for progress.
    SESSION_TYPE = 8  # Session type (what entity caused the operation).
    INTEGER_DATA = 10  # Integer data.
    OBJECT_ID = 11  # Object ID (note this is a string).
    OBJECT_TYPE = 12  # Object type.
    OBJECT_NAME = 13  # Object name.
    OBJECT_PATH = 14  # Object path. A comma-separated list of parents, starting with the object's parent.
    SEVERITY = 22  # Severity level of an exception.
    SUCCESS = 23  # 1 = success. 0 = failure (for example, a 1 means success of a permissions check and a 0 means a failure of that check).
    ERROR = 24  # Error number of a given event.
    CONNECTION_ID = 25  # Unique connection ID.
    DATABASE_NAME = 28  # Name of the database in which the statement of the user is running.
    CLIENT_PROCESS_ID = 36  # The process ID of the client application.
    SESSION_ID = 39  # Session GUID.
    TEXT_DATA = 42  # Text data associated with the event.
    SERVER_NAME = 43  # Name of the server producing the event.
    ACTIVITY_ID = 46
    REQUEST_ID = 47
