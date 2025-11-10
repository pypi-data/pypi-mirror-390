from enum import Enum


class NotificationColumns(Enum):
    EVENT_CLASS = 0  # Event Class is used to categorize events.
    EVENT_SUBCLASS = 1  # Event Subclass provides additional information about each event class. The following Sub Class Id: Sub Class Name pairs are defined: 0: Proactive Caching Begin 1: Proactive Caching End 2: Flight Recorder Started 3: Flight Recorder Stopped 4: Configuration Properties Updated 5: SQL Trace 6: Object Created 7: Object Deleted 8: Object Altered 9: Proactive Caching Polling Begin 10: Proactive Caching Polling End 11: Flight Recorder Snapshot Begin 12: Flight Recorder Snapshot End 13: Proactive Caching: notifiable object updated 14: Lazy Processing: start processing 15: Lazy Processing: processing complete 16: SessionOpened Event Begin 17: SessionOpened Event End 18: SessionClosing Event Begin 19: SessionClosing Event End 20: CubeOpened Event Begin 21: CubeOpened Event End 22: CubeClosing Event Begin 23: CubeClosing Event End 24: Transaction abort requested
    CURRENT_TIME = 2  # Contains the current time of the notification event, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    START_TIME = 3  # Contains the time at which the event started, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    END_TIME = 4  # Contains the time at which the event ended. This column is not populated for starting event classes, such as SQL:BatchStarting or SP:Starting. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    DURATION = 5  # Contains the amount of time (in milliseconds) taken by the event.
    INTEGER_DATA = 10  # Contains the integer data associated with the notification event. When the EventSubclass column is 8, values are: 1 = Created 2 = Deleted 3 = Changed object's properties 4 = Changed properties of the object's children 6 = Children added 7 = Children deleted 8 = Object fully processed 9 = Object partially processed 10 = Object unprocessed 11 = Object fully optimized 12 = Object partially optimized 13 = Object not optimized
    OBJECT_ID = 11  # Contains the Object ID for which this notification is issued; this is a string value.
    OBJECT_TYPE = 12  # Contains the object type associated with the notification event.
    OBJECT_NAME = 13  # Contains the object name associated with the notification event.
    OBJECT_PATH = 14  # Contains the object path associated with the notification event. The path is returned as a comma-separated list of parents, starting with the object's parent.
    OBJECT_REFERENCE = 15  # Contains the object reference for the progress report end event. The object reference is encoded as XML by all parents by using tags to describe the object.
    CONNECTION_ID = 25  # Contains the unique connection ID associated with the notification event.
    DATABASE_NAME = 28  # Contains the name of the database in which the notification event occurred.
    NT_USER_NAME = 32  # Contains the user name associated with the command event. Depending on the environment, the user name is in the following form: - Windows user account (DOMAIN\UserName) - User Principal Name (UPN) (username@domain.com) - Service  Principal Name (SPN) (appid@tenantid) - Power BI Service Account  (Power BI Service) - Power BI Service on behalf of a UPN or SPN (Power BI Service (UPN/SPN))
    NT_DOMAIN_NAME = 33  # Contains the domain name associated with the user account that triggered the command event.  - Windows domain name for Windows user accounts - AzureAD for Microsoft Entra accounts - NT AUTHORITY accounts without a Windows domain name, such as the Power BI service
    SESSION_ID = 39  # Contains the session ID associated with the notification event.
    NT_CANONICAL_USER_NAME = 40  # Contains the user name associated with the command event. Depending on the environment, the user name is in the following form: - Windows user account (DOMAIN\UserName) - User Principal Name (UPN) (username@domain.com) - Service Principal Name (SPN) (appid@tenantid) - Power BI Service Account (Power BI Service)
    SP_ID = 41  # Contains the server process ID (SPID) that uniquely identifies the user session associated with the notification event. The SPID directly corresponds to the session GUID used by XMLA.
    TEXT_DATA = 42  # Contains the text data associated with the notification event.
    SERVER_NAME = 43  # Contains the name of the Analysis Services instance on which the notification event occurred.
    REQUEST_PROPERTIES = 45  # Contains the properties of the XMLA request.
    ACTIVITY_ID = 46
    REQUEST_ID = 47


class UserDefinedColumns(Enum):
    EVENT_CLASS = 0  # Event Class is used to categorize events.
    EVENT_SUBCLASS = 1  # A specific user event subclass that provides additional information about each event class.
    CURRENT_TIME = 2  # Contains the current time of the notification event, when available. For filtering, expected formats are 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'.
    INTEGER_DATA = 10  # A specific user defined event information.
    CONNECTION_ID = 25  # Contains the unique connection ID associated with the notification event.
    DATABASE_NAME = 28  # Contains the name of the database in which the notification event occurred.
    NT_USER_NAME = 32  # Contains the user name associated with the command event. Depending on the environment, the user name is in the following form: - Windows user account (DOMAIN\UserName) - User Principal Name (UPN) (username@domain.com) - Service  Principal Name (SPN) (appid@tenantid) - Power BI Service Account  (Power BI Service) - Power BI Service on behalf of a UPN or SPN (Power BI Service (UPN/SPN))
    NT_DOMAIN_NAME = 33  # Contains the domain name associated with the user account that triggered the command event.  - Windows domain name for Windows user accounts - AzureAD for Microsoft Entra accounts - NT AUTHORITY accounts without a Windows domain name, such as the Power BI service
    SESSION_ID = 39  # Contains the session ID associated with the notification event.
    NT_CANONICAL_USER_NAME = 40  # Contains the Windows user name associated with the notification event. The user name is in canonical form. For example, engineering.microsoft.com/software/user.
    SP_ID = 41  # Contains the server process ID (SPID) that uniquely identifies the user session associated with the notification event. The SPID directly corresponds to the session GUID used by XMLA.
    TEXT_DATA = 42  # Contains the text data associated with the notification event.
    SERVER_NAME = 43  # Contains the name of the Analysis Services instance on which the notification event occurred.
    ACTIVITY_ID = 46
    REQUEST_ID = 47
