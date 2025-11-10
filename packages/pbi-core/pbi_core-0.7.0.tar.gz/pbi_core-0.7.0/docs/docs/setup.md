This library can be run without any setup if PowerBI Desktop is already running, as it can connect to the SSAS instance started by PowerBI Desktop. However, you can also set up the library to automatically setup the necessary SSAS programs when it cannot find a running SSAS instance.

There are currently two setup options:

1. EXE Setup (Recommended)
2. MSMDSRV Setup (Broken)


!!! note "Pre-Setup Requirement"

    These setups assume that the user has PowerBI Desktop installed on their machine.

## EXE Setup (Recommended)

Steps:

1. Run the following command in your terminal:

   ```bash
   python -m pbi_core setup
   ```

2. You will be prompted to `Select startup configuration type (msmdsrv/exe)`. Choose `exe`.
3. The temp workspaces are not currently used when using the `exe` setup, so you can just press Enter to accept the default.
4. Enter the path to your PowerBI Desktop executable when prompted. When possible, the script will attempt to locate it automatically. You can find it by opening the file location of the PowerBI Desktop shortcut. On Windows, it might be something like:

   ```
   C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe
   ```

### Verifying correct setup

Close all instances of PowerBI Desktop and run the script [here](quick_start.md#basic-functionality) to verify that the setup was successful. There should be no errors in the terminal and you should see a new PowerBI Desktop  window open.

## MSMDSRV Setup (Broken)

Steps:

1. Run the following command in your terminal:

   ```bash
   python -m pbi_core setup
   ```

2. You will be prompted to `Select startup configuration type (msmdsrv/exe)`. Choose `msmdsrv`.
3. Press Enter to accept the default temp workspaces. This will be the folder where the necessary SSAS config files are stored. These files are temporay and linked to the specific instance of SSAS running. You shouldn't need to explore this folder manually.
4. Open a report in PowerBI Desktop. This will start an SSAS instance that we can use as a template.
   - `msmdsrv.ini path`: You must find the `AnalysisServicesWorkspaces` folder and then choose any subfolder. This file should be in this folder. Copy the full path of this file. 
  
        ```
        C:/Users/{os.getlogin()}/Microsoft/Power BI Desktop Store App/AnalysisServicesWorkspaces/<UUID>
        ```
    - `bin folder path`: This is the folder where the `msmdsrv.exe` file is located. This is usually in the `bin` folder of your PowerBI Desktop installation. Copy the full path of this folder. You can find it by opening the file location of the PowerBI Desktop shortcut. It is usually something like:
  
        ```
        C:/Program Files/Microsoft Power BI Desktop/bin
        ```
    - `CertifiedExtensions folder path`: This is the folder where the `CertifiedExtensions` folder is located. This is usually in the main installation folder of your PowerBI Desktop installation. Copy the full path of this folder. You can find it by opening the file location of the PowerBI Desktop shortcut. It is usually something like:
  
        ```
        C:/Program Files/Microsoft Power BI Desktop/CertifiedExtensions
        ```

### Verifying correct setup

Close all instances of PowerBI Desktop and run the script [here](quick_start.md#basic-functionality) to verify that the setup was successful. There should be no errors in the terminal and you should see **no** PowerBI Desktop  window open.