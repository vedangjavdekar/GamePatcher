import subprocess
import sys
import shutil

from pathlib import Path

import wx
import wx.lib.inspection
import wx.lib.newevent

import app_version
import buildInfo
import buildProcess
import pathUtils
import tarUtils
import errorCodes

errorColor = None
normalColor = None
successColor = None
errorFont = None
defaultFont = None
logFont = None

INITIAL_CHECKS = "InitialChecks"
FILE_CHECKS = "DiffFiles"
CREATE_TAR = "CreateTar"
UPLOAD_ARCHIVE = "UploadArchive"
VERSION_INC = "VersionInc"

validation = {INITIAL_CHECKS: 0, FILE_CHECKS: 0, UPLOAD_ARCHIVE: 0, VERSION_INC: 0}

UpdateStateEvent, EVT_UPDATE_STATE = wx.lib.newevent.NewEvent()
ResetEvent, EVT_RESET = wx.lib.newevent.NewEvent()


class RedirectText(object):
    def __init__(self, aWxTextCtrl):
        self.out = aWxTextCtrl

    def write(self, string):
        self.out.WriteText(string)


class CustomPanelBase(wx.Panel):
    def __init__(self, frame, parent, build):
        super().__init__(parent)
        self.frame = frame
        self.build = build
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetFont(defaultFont)
        self.onInit()
        self.SetSizer(self.sizer)

    def onInit(self):
        pass

    def onStateUpdate(self, evt):
        pass

    def onReset(self, build):
        self.build = build

    def performTask(self, evt=None):
        pass


class LogPanel(CustomPanelBase):
    def __init__(self, frame, parent, build):
        super().__init__(frame, parent, build)

    def onInit(self):
        self.log = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        )
        self.log.SetFont(logFont)

        redir = RedirectText(self.log)
        sys.stdout = redir

        logHSizer = wx.BoxSizer(wx.HORIZONTAL)

        logHeading = wx.StaticText(self, wx.ID_ANY, "Logs:")
        boldFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        logHeading.SetFont(boldFont)

        clearLogsBtn = wx.Button(
            self,
            wx.ID_ANY,
            "Clear",
        )

        # Heading
        logHSizer.Add(logHeading, 1, wx.ALL | wx.ALIGN_CENTER, 10)
        # SPACER
        logHSizer.Add((0, 0), 1, wx.EXPAND)
        # Button
        logHSizer.Add(clearLogsBtn, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 10)

        self.sizer.Add(logHSizer, 0, wx.EXPAND)

        self.sizer.Add(
            self.log,
            1,
            flag=wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT,
            border=10,
        )

        self.SetMinSize((600, 200))

        clearLogsBtn.Bind(wx.EVT_BUTTON, self.onClearLogs)

    def getTextWidget(self):
        return self.log

    def onClearLogs(self, event):
        self.log.SetLabelText("")
        event.Skip()


class DirectoryPanel(CustomPanelBase):
    def __init__(self, frame, parent, build, src, dst):
        self.src = src
        self.dst = dst
        super().__init__(frame, parent, build)

    def onReset(self, build, src, dst):
        super().onReset(build)
        self.src = src
        self.dst = dst
        self.tSrcDir.SetLabelText(f"Prev: {self.src}")
        self.tDstDir.SetLabelText(f"Curr: {self.dst}")

    def onInit(self):
        self.tSrcDir = wx.StaticText(self)
        self.tSrcDir.SetForegroundColour(successColor)
        self.sizer.Add(self.tSrcDir, flag=wx.LEFT, border=10)

        self.tDstDir = wx.StaticText(self)
        self.tDstDir.SetForegroundColour(successColor)
        self.sizer.Add(self.tDstDir, flag=wx.LEFT, border=10)

    def performTask(self, evt=None):
        dirsExist = True
        errStrs = []
        ecode = errorCodes.NO_ERROR

        if self.src == "":
            self.tSrcDir.SetFont(errorFont)
            self.tSrcDir.SetForegroundColour(errorColor)
            errStrs.append("[ERROR]: previous version directory not found.")
            dirsExist &= False
            ecode = errorCodes.PATH_ERROR
        else:
            self.tSrcDir.SetFont(defaultFont)
            self.tSrcDir.SetForegroundColour(normalColor)

        if self.dst == "":
            self.tDstDir.SetFont(errorFont)
            self.tDstDir.SetForegroundColour(errorColor)
            errStrs.append(
                f"[ERROR]: Looks like shipping build was not created for {self.build.current_version.version_string}"
            )
            dirsExist &= False
            ecode = errorCodes.PATH_ERROR
        else:
            self.tDstDir.SetFont(defaultFont)
            self.tDstDir.SetForegroundColour(normalColor)

        if dirsExist:
            if not pathUtils.checkVersionBinDir(self.build.current_version):
                errStrs.append(
                    f"[ERROR]: Version Files for {self.build.current_version.version_string} can't be found."
                )
                ecode = errorCodes.FILE_NOT_FOUND_ERROR
            if self.build.prev_version.is_valid():
                if not pathUtils.checkVersionStagingDir(self.build.prev_version):
                    errStrs.append(
                        f"[ERROR]: Version Archive for {self.build.prev_version.version_string} can't be found."
                    )
                    ecode = errorCodes.FILE_NOT_FOUND_ERROR
            else:
                print(
                    "[INFO]: No previous build found, this is the first time building the project."
                )

        if len(errStrs):
            self.frame.SetStatusText(errorCodes.ERROR_CODES[ecode])
            validation[INITIAL_CHECKS] = -1

            for err in errStrs:
                print(err)
        else:
            validation[INITIAL_CHECKS] = 1

        evt = UpdateStateEvent()
        wx.PostEvent(self.frame, evt)


class DiffPanel(CustomPanelBase):
    def __init__(self, frame, parent, build, src, dst):
        self.src = src
        self.dst = dst
        super().__init__(frame, parent, build)

    def onReset(self, build, src, dst):
        super().onReset(build)
        self.src = src
        self.dst = dst

    def onInit(self):
        self.diffFileButton = wx.Button(self, wx.ID_ANY, "Diff Files")
        self.diffFileButton.Bind(wx.EVT_BUTTON, self.performTask)
        self.createTarButton = wx.Button(self, wx.ID_ANY, "Create Archive")
        self.createTarButton.Bind(wx.EVT_BUTTON, self.performTask)
        self.uploadTarButton = wx.Button(self, wx.ID_ANY, "Upload To Server")
        self.uploadTarButton.Bind(wx.EVT_BUTTON, self.performTask)

        self.sizer.Add(self.diffFileButton, 0, wx.EXPAND, 5)
        self.sizer.Add(self.createTarButton, 0, wx.EXPAND, 5)
        self.sizer.Add(self.uploadTarButton, 0, wx.EXPAND, 5)

    def onStateUpdate(self, evt):
        self.diffFileButton.Enable(validation[INITIAL_CHECKS] == 1)
        self.createTarButton.Enable(validation[FILE_CHECKS] >= 1)
        self.uploadTarButton.Enable(validation[FILE_CHECKS] == 2)

    def performTask(self, evt=None):
        shouldGenerateEvent = False
        ecode = errorCodes.NO_ERROR
        if validation[FILE_CHECKS] <= 0:
            ecode = buildProcess.get_diff_directory_result(
                self.build, self.src, self.dst
            )
            if ecode == errorCodes.NO_ERROR:
                validation[FILE_CHECKS] = 1
                shouldGenerateEvent = True

        elif validation[FILE_CHECKS] == 1:
            ecode = tarUtils.create_archive(self.build.current_version)
            if ecode == errorCodes.NO_ERROR:
                validation[FILE_CHECKS] = 2
                shouldGenerateEvent = True

        elif validation[FILE_CHECKS] == 2:
            ecode = buildProcess.upload_build_to_server(self.build.current_version)
            if ecode == errorCodes.NO_ERROR:
                validation[FILE_CHECKS] = 3
                shouldGenerateEvent = True

        evt.Skip()
        if shouldGenerateEvent:
            evt = UpdateStateEvent()
            wx.PostEvent(self.frame, evt)

        self.frame.SetStatusText(errorCodes.ERROR_CODES[ecode])


class VersionIncrementPanel(CustomPanelBase):
    def __init__(self, frame, parent, build):
        super().__init__(frame, parent, build)

    def onReset(self, build):
        super().onReset(build)

    def onInit(self):
        incVersionBtn = wx.Button(self, wx.ID_ANY, "Increment Version")
        incVersionBtn.Bind(wx.EVT_BUTTON, self.performTask)

        self.incMajorCB = wx.CheckBox(self, wx.ID_ANY, "Increment Major Version")

        self.sizer.Add(incVersionBtn, 1, wx.EXPAND, 5)
        self.sizer.Add(self.incMajorCB, 1, wx.EXPAND, 5)

    def onStateUpdate(self, evt):
        self.Enable(validation[FILE_CHECKS] >= 3)

    def performTask(self, evt=None):
        ecode, version_saved = buildProcess.increment_version(
            self.build, self.incMajorCB.GetValue()
        )
        if ecode == errorCodes.NO_ERROR:
            validation[VERSION_INC] = 1

            if version_saved:
                evt = UpdateStateEvent()
                wx.PostEvent(self.frame, evt)

        self.frame.SetStatusText(errorCodes.ERROR_CODES[ecode])


class CleanUpPanel(CustomPanelBase):
    def __init__(self, frame, parent, build):
        super().__init__(frame, parent, build)

    def onReset(self, build):
        super().onReset(build)
        self.tCurrMajVersion.SetValue(self.build.current_version.major)
        self.tCurrMinVersion.SetValue(self.build.current_version.minor)

    def onInit(self):
        hbox1 = wx.GridBagSizer(2, 7)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.tCurrMajVersion = wx.SpinCtrl(self, wx.ID_ANY)
        self.tCurrMajVersion.SetMin(1)

        self.tCurrMinVersion = wx.SpinCtrl(self, wx.ID_ANY)
        self.tCurrMinVersion.SetMin(0)

        self.setCurrVersionBtn = wx.Button(self, wx.ID_ANY, label="Set")
        self.deleteCurrVersionBtn = wx.Button(self, wx.ID_ANY, label="Delete")

        self.tPrevMajVersion = wx.SpinCtrl(self, wx.ID_ANY)
        self.tPrevMajVersion.SetMin(1)

        self.tPrevMinVersion = wx.SpinCtrl(self, wx.ID_ANY)
        self.tPrevMinVersion.SetMin(0)

        self.setPrevVersionBtn = wx.Button(self, wx.ID_ANY, label="Set")
        self.deletePrevVersionBtn = wx.Button(self, wx.ID_ANY, label="Delete")

        hbox1.Add(
            wx.StaticText(self, id=wx.ID_ANY, label="Set Current Version:"),
            pos=(0, 0),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )
        hbox1.Add(
            wx.StaticText(self, id=wx.ID_ANY, label="Major"),
            pos=(0, 1),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )
        hbox1.Add(
            self.tCurrMajVersion,
            pos=(0, 2),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )
        hbox1.Add(
            wx.StaticText(self, id=wx.ID_ANY, label="Minor"),
            pos=(0, 3),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )
        hbox1.Add(
            self.tCurrMinVersion,
            pos=(0, 4),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )
        hbox1.Add(
            self.setCurrVersionBtn,
            pos=(0, 5),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )
        hbox1.Add(
            self.deleteCurrVersionBtn,
            pos=(0, 6),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )

        hbox1.Add(
            wx.StaticText(self, id=wx.ID_ANY, label="Set Prev Version:"),
            pos=(1, 0),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )
        hbox1.Add(
            wx.StaticText(self, id=wx.ID_ANY, label="Major"),
            pos=(1, 1),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )
        hbox1.Add(
            self.tPrevMajVersion,
            pos=(1, 2),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )
        hbox1.Add(
            wx.StaticText(self, id=wx.ID_ANY, label="Minor"),
            pos=(1, 3),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )
        hbox1.Add(
            self.tPrevMinVersion,
            pos=(1, 4),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )
        hbox1.Add(
            self.setPrevVersionBtn,
            pos=(1, 5),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )
        hbox1.Add(
            self.deletePrevVersionBtn,
            pos=(1, 6),
            flag=wx.LEFT | wx.RIGHT,
            border=5,
        )

        self.deleteArchiveBtn = wx.Button(
            self, wx.ID_ANY, label="Delete Current Archive"
        )
        self.deleteShippingBuildBtn = wx.Button(
            self, wx.ID_ANY, label="Delete Current Shipping Build"
        )

        hbox2.Add(self.deleteArchiveBtn, 1)
        hbox2.Add(self.deleteShippingBuildBtn, 1)

        self.sizer.Add(hbox1, 1, wx.EXPAND, 5)
        self.sizer.Add(hbox2, 1, wx.EXPAND | wx.TOP, 10)

        self.setCurrVersionBtn.Bind(wx.EVT_BUTTON, self.setCurrVersion)
        self.setPrevVersionBtn.Bind(wx.EVT_BUTTON, self.setPrevVersion)
        self.deleteCurrVersionBtn.Bind(wx.EVT_BUTTON, self.deleteCurrVersion)
        self.deleteCurrVersionBtn.Bind(wx.EVT_BUTTON, self.deleteCurrVersion)
        self.deleteShippingBuildBtn.Bind(wx.EVT_BUTTON, self.deleteShippingBuild)
        self.deleteArchiveBtn.Bind(wx.EVT_BUTTON, self.deleteArchive)

    def setCurrVersion(self, evt=None):
        ver = buildInfo.VersionInfo()

        ver.major = self.tCurrMajVersion.GetValue()
        ver.minor = self.tCurrMinVersion.GetValue()
        ver.major = max(ver.major, 1)
        ver.minor = max(ver.minor, 0)

        ver.create_version_string()

        app_version.save(ver, pathUtils.CURR_VERSION_FILE)

        evt = ResetEvent(generateProject=True)
        wx.PostEvent(self.frame, evt)

    def deleteCurrVersion(self, evt=None):
        filepath = Path(pathUtils.CURR_VERSION_FILE)
        if filepath.exists():
            filepath.unlink()
            print("[SUCCESS]: Config deleted successfully!")
        else:
            print("[INFO]: File doesn't exist.")

        evt = ResetEvent(generateProject=True)
        wx.PostEvent(self.frame, evt)

    def setPrevVersion(self, evt=None):
        ver = buildInfo.VersionInfo()

        ver.major = self.tPrevMajVersion.GetValue()
        ver.minor = self.tPrevMinVersion.GetValue()
        ver.major = max(ver.major, 1)
        ver.minor = max(ver.minor, 0)

        ver.create_version_string()

        app_version.save(ver, pathUtils.PREV_VERSION_FILE)
        evt = ResetEvent()
        wx.PostEvent(self.frame, evt)

    def deletePrevVersion(self, evt=None):
        filepath = Path(pathUtils.PREV_VERSION_FILE)
        if filepath.exists():
            filepath.unlink()
            print("[SUCCESS]: Config deleted successfully!")
            evt = ResetEvent()
            wx.PostEvent(self.frame, evt)
        else:
            print("[INFO]: File doesn't exist.")

    def deleteArchive(self, evt=None):
        filepath = Path(pathUtils.get_tar_filepath(self.build.prev_version))
        if filepath.exists():
            filepath.unlink()
            print("[SUCCESS]: Archive deleted successfully!")
            evt = ResetEvent()
            wx.PostEvent(self.frame, evt)
        else:
            print("[ERROR]: Archive not found")
            self.frame.SetStatusText(
                errorCodes.ERROR_CODES[errorCodes.FILE_NOT_FOUND_ERROR]
            )

    def deleteShippingBuild(self, evt=None):
        dirpath = Path(pathUtils.get_shipping_build_dir(self.build.current_version))
        if dirpath.exists():
            shutil.rmtree(dirpath)
            print("[SUCCESS]: Shipping Build deleted successfully!")
            evt = ResetEvent()
            wx.PostEvent(self.frame, evt)
        else:
            print("[ERROR]: Shipping Build not found")


class BuildGUI(wx.Frame):
    def __init__(self):
        self.stateUpdatePanels = []

        wx.Frame.__init__(self, None, wx.ID_ANY, title="BUILD HELPER")
        self.CreateStatusBar()

        # Menu Bar
        menubar = wx.MenuBar()

        file_menu = wx.Menu()
        file_menu.Append(wx.ID_FILE, "Generate Project Files")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "Exit")

        menubar.Append(file_menu, "File")

        self.SetMenuBar(menubar)

        panel = wx.Panel(self)
        pboxSizer = wx.BoxSizer(wx.VERTICAL)
        self.build = None
        self.src_root_dir = ""
        self.dst_root_dir = ""

        # LOG PANEL
        logPanel = LogPanel(self, panel, self.build)

        self.buildText = wx.StaticText(panel)

        resetBtn = wx.Button(panel, wx.ID_ANY, label="Reset")

        topBar = wx.BoxSizer(wx.HORIZONTAL)
        topBar.Add(self.buildText, 0, flag=wx.EXPAND | wx.ALL, border=5)
        topBar.Add((0, 0), 1, wx.EXPAND)
        topBar.Add(resetBtn, 0, flag=wx.EXPAND | wx.ALL, border=5)

        # DIRECTORY PANEL
        self.dirPanel = DirectoryPanel(
            self, panel, self.build, self.src_root_dir, self.dst_root_dir
        )

        # DIFF PANEL
        self.diffPanel = DiffPanel(
            self, panel, self.build, self.src_root_dir, self.dst_root_dir
        )

        # VERSION INC PANEL
        self.versionIncPanel = VersionIncrementPanel(self, panel, self.build)

        # CLEANUP PANEL
        self.cleanupPanel = CleanUpPanel(self, panel, self.build)

        pboxSizer.Add(topBar, 0, wx.EXPAND)
        pboxSizer.Add(wx.StaticLine(panel), flag=wx.EXPAND | wx.BOTTOM, border=10)

        # directory panel
        pboxSizer.Add(self.dirPanel, flag=wx.EXPAND | wx.ALL, border=10)

        pboxSizer.Add(wx.StaticLine(panel), flag=wx.EXPAND | wx.BOTTOM, border=10)

        pboxSizer.Add(
            wx.StaticText(panel, wx.ID_ANY, "Diffing Controls:"),
        )
        # diff panel
        pboxSizer.Add(self.diffPanel, 0, flag=wx.EXPAND | wx.ALL, border=10)

        pboxSizer.Add(wx.StaticLine(panel), flag=wx.EXPAND | wx.BOTTOM, border=10)

        pboxSizer.Add(
            wx.StaticText(panel, wx.ID_ANY, "Version Controls:"),
        )

        # version increment panel
        pboxSizer.Add(self.versionIncPanel, 0, flag=wx.EXPAND | wx.ALL, border=10)

        pboxSizer.Add(wx.StaticLine(panel), flag=wx.EXPAND | wx.BOTTOM, border=10)
        pboxSizer.Add(
            wx.StaticText(panel, wx.ID_ANY, "Cleanup Controls:"),
        )
        pboxSizer.Add(self.cleanupPanel, 0, flag=wx.EXPAND | wx.ALL, border=10)

        pboxSizer.Add(logPanel, 1, flag=wx.EXPAND | wx.ALL, border=10)
        panel.SetSizer(pboxSizer)
        pboxSizer.Fit(self)

        # Restrict Window Resize to vertical axis
        self.SetMinSize(self.GetSize())
        self.targetWidth = self.GetSize()[0]
        self.SetMaxSize((self.targetWidth, -1))
        self.Center()

        # Event Propagation
        self.stateUpdatePanels.append(self.dirPanel)
        self.stateUpdatePanels.append(self.diffPanel)
        self.stateUpdatePanels.append(self.versionIncPanel)

        # Event Handling
        self.Bind(EVT_UPDATE_STATE, self.handleStatusUpdate)
        resetBtn.Bind(wx.EVT_BUTTON, self.handleReset)
        self.Bind(EVT_RESET, self.handleReset)

        self.Bind(wx.EVT_MENU, self.handleGenerateProjectFiles, id=wx.ID_FILE)
        self.Bind(wx.EVT_MENU, self.handleExit, id=wx.ID_EXIT)

        self.handleReset()
        return

    def handleStatusUpdate(self, evt):
        for panel in self.stateUpdatePanels:
            panel.onStateUpdate(evt)

        if validation[VERSION_INC] == 1:
            self.handleGenerateProjectFiles()
            self.handleReset()
        evt.Skip()

    def handleReset(self, evt=None):
        self.handleGenerateProjectFiles()
        global validation

        validation = dict.fromkeys(validation, 0)

        self.build = buildInfo.Build()
        buildProcess.load_version_info(self.build)

        self.src_root_dir, self.dst_root_dir = buildProcess.get_directories(
            self.build.current_version
        )

        self.buildText.SetLabelText(
            f"BUILDING: {self.build.current_version.version_string}"
        )

        self.dirPanel.onReset(self.build, self.src_root_dir, self.dst_root_dir)
        self.diffPanel.onReset(self.build, self.src_root_dir, self.dst_root_dir)
        self.versionIncPanel.onReset(self.build)
        self.cleanupPanel.onReset(self.build)

        self.dirPanel.performTask()

    def handleExit(self, evt):
        self.Close()

    def handleGenerateProjectFiles(self, evt=None):
        devDir = Path(__file__).parent.parent.absolute().resolve()
        try:
            result = subprocess.run(
                [str(devDir) + "\\GenerateProjectFiles.bat"],
                cwd=devDir,
                check=True,
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            print("[SUCCESS]: Project Files are generated successfully!")
        except subprocess.CalledProcessError as e:
            print("Generating Project Files failed with return code:", e.returncode)


# Run the program
if __name__ == "__main__":
    app = wx.App(False)

    errorColor = wx.Colour(255, 0, 0)
    normalColor = wx.Colour(0, 0, 0)
    successColor = wx.Colour(27, 181, 24)
    errorFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
    defaultFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
    logFont = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

    # wx.lib.inspection.InspectionTool().Show()

    frame = BuildGUI().Show()
    app.MainLoop()
