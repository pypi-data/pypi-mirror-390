from enum import Enum


class ExistingConnectionColumns(Enum):
    CURRENT_TIME = 2  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    START_TIME = 3  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    CONNECTION_ID = 25  # Unique connection ID.
    NT_USER_NAME = 32  # Contains the user name associated with the command event. Depending on the environment, the user name is in the following form: - Windows user account (DOMAIN\UserName) - User Principal Name (UPN) (username@domain.com) - Service  Principal Name (SPN) (appid@tenantid) - Power BI Service Account  (Power BI Service) - Power BI Service on behalf of a UPN or SPN (Power BI Service (UPN/SPN))
    NT_DOMAIN_NAME = 33  # Contains the domain name associated with the user account that triggered the command event.  - Windows domain name for Windows user accounts - AzureAD for Microsoft Entra accounts - NT AUTHORITY accounts without a Windows domain name, such as the Power BI service
    CLIENT_HOST_NAME = 35  # Name of the computer on which the client is running. This data column is populated if the host name is provided by the client.
    CLIENT_PROCESS_ID = 36  # The process ID of the client application.
    APPLICATION_NAME = 37  # Name of the client application that created the connection to the server. This column is populated with the values passed by the application rather than the displayed name of the program.
    SP_ID = 41  # Server process ID. This uniquely identifies a user session. This directly corresponds to the session GUID used by XML/A.
    SERVER_NAME = 43  # Name of the server producing the event.
    ACTIVITY_ID = 46
    REQUEST_ID = 47


class ExistingSessionColumns(Enum):
    CURRENT_TIME = 2  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    START_TIME = 3  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    DURATION = 5  # Amount of time (in milliseconds) taken by the event.
    CPU_TIME = 6  # Amount of CPU time (in milliseconds) used by the event.
    CONNECTION_ID = 25  # Unique connection ID.
    DATABASE_NAME = 28  # Name of the database in which the statement of the user is running.
    NT_USER_NAME = 32  # Contains the user name associated with the command event. Depending on the environment, the user name is in the following form: - Windows user account (DOMAIN\UserName) - User Principal Name (UPN) (username@domain.com) - Service  Principal Name (SPN) (appid@tenantid) - Power BI Service Account  (Power BI Service) - Power BI Service on behalf of a UPN or SPN (Power BI Service (UPN/SPN))
    NT_DOMAIN_NAME = 33  # Contains the domain name associated with the user account that triggered the command event.  - Windows domain name for Windows user accounts - AzureAD for Microsoft Entra accounts - NT AUTHORITY accounts without a Windows domain name, such as the Power BI service
    CLIENT_HOST_NAME = 35  # Name of the computer on which the client is running. This data column is populated if the host name is provided by the client.
    CLIENT_PROCESS_ID = 36  # The process ID of the client application.
    APPLICATION_NAME = 37  # Name of the client application that created the connection to the server. This column is populated with the values passed by the application rather than the displayed name of the program.
    NT_CANONICAL_USER_NAME = 40  # Contains the user name associated with the command event. Depending on the environment, the user name is in the following form: - Windows user account (DOMAIN\UserName) - User Principal Name (UPN) (username@domain.com) - Service Principal Name (SPN) (appid@tenantid) - Power BI Service Account (Power BI Service)
    SP_ID = 41  # Server process ID. This uniquely identifies a user session. This directly corresponds to the session GUID used by XML/A.
    TEXT_DATA = 42  # Text data associated with the event.
    SERVER_NAME = 43  # Name of the server producing the event.
    REQUEST_PROPERTIES = 45  # XMLA request properties.
    ACTIVITY_ID = 46
    REQUEST_ID = 47


class SessionInitializeColumns(Enum):
    CURRENT_TIME = 2  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    START_TIME = 3  # Time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    CONNECTION_ID = 25  # Unique connection ID.
    DATABASE_NAME = 28  # Name of the database in which the statement of the user is running.
    NT_USER_NAME = 32  # Contains the user name associated with the command event. Depending on the environment, the user name is in the following form: - Windows user account (DOMAIN\UserName) - User Principal Name (UPN) (username@domain.com) - Service  Principal Name (SPN) (appid@tenantid) - Power BI Service Account  (Power BI Service) - Power BI Service on behalf of a UPN or SPN (Power BI Service (UPN/SPN))
    NT_DOMAIN_NAME = 33  # Contains the domain name associated with the user account that triggered the command event.  - Windows domain name for Windows user accounts - AzureAD for Microsoft Entra accounts - NT AUTHORITY accounts without a Windows domain name, such as the Power BI service
    CLIENT_HOST_NAME = 35  # Name of the computer on which the client is running. This data column is populated if the host name is provided by the client.
    CLIENT_PROCESS_ID = 36  # The process ID of the client application.
    APPLICATION_NAME = 37  # Name of the client application that created the connection to the server. This column is populated with the values passed by the application rather than the displayed name of the program.
    NT_CANONICAL_USER_NAME = 40  # Contains the user name associated with the command event. Depending on the environment, the user name is in the following form: - Windows user account (DOMAIN\UserName) - User Principal Name (UPN) (username@domain.com) - Service Principal Name (SPN) (appid@tenantid) - Power BI Service Account (Power BI Service)
    SP_ID = 41  # Server process ID. This uniquely identifies a user session. This directly corresponds to the session GUID used by XML/A.
    TEXT_DATA = 42  # Text data associated with the event.
    SERVER_NAME = 43  # Name of the server producing the event.
    REQUEST_PROPERTIES = 45  # XMLA request properties.
    ACTIVITY_ID = 46
    REQUEST_ID = 47
