import express, { query } from "express";
import fs from "fs";
import path from "path";
import { openConnection } from "./database.mjs";
import tar from "tar";
import { assert } from "console";
import { version } from "os";

const router = express.Router();

const runDBQueries = true;
const buildsPath = "builds/";
const deleteFilesName = "deleteFiles.json";
const tempDirPath = "temp/";
const deleteFilesPath = buildsPath + tempDirPath + deleteFilesName;

const getVersionDetails = async (db, queryParams) => {
	const curr = queryParams.curr;
	const update = queryParams.update;
	if (curr === undefined) {
		return {
			curr: "",
			update: "",
			isValid: false,
		};
	} else {
		let result = {
			curr,
			update,
			isValid: false,
		};

		const currVer = await db.get(
			`SELECT VersionString
				FROM BuildInfo
				WHERE VersionString='${curr}'`
		);

		if (currVer === undefined) {
			return {
				curr: "",
				update: "",
				isValid: false,
			};
		} else {
			result.curr = currVer.VersionString;
		}

		let updateVersionQuery = "";
		if (result.update === undefined) {
			updateVersionQuery = `SELECT VersionString
					FROM BuildInfo 
					ORDER BY ReleaseDate DESC`;
		} else {
			updateVersionQuery = `SELECT VersionString
				FROM BuildInfo
				WHERE VersionString='${result.update}'`;
		}
		const updateVer = await db.get(updateVersionQuery);
		if (updateVer === undefined) {
			return {
				curr: "",
				update: "",
				isValid: false,
			};
		} else {
			result.update = updateVer.VersionString;
		}

		result.isValid = true;
		return result;
	}
};

const downloadVersion = async (res, versionString) => {
	console.log(`downloading ${versionString}`);
	await tar.create(
		{
			gzip: true,
			file: buildsPath + "game.tar.gz",
			C: buildsPath + versionString,
		},
		["."]
	);

	res.download(buildsPath + "game.tar.gz", (err) => {
		if (err) {
			console.log(err);
		} else {
			console.log("Download success");
		}

		fs.unlinkSync(buildsPath + "game.tar.gz");
	});
};

const downloadFiles = async (res, files) => {
	for (var property in files.downloadFilePaths) {
		const filePaths = files.downloadFilePaths[property];
		for (var fileIndex = 0; fileIndex < filePaths.length; ++fileIndex) {
			const filePath = buildsPath + property + filePaths[fileIndex];
			const dirName = path.dirname(filePaths[fileIndex]).replace("\\", "/");
			if (dirName !== ".") {
				fs.mkdirSync(buildsPath + tempDirPath + dirName, { recursive: true });
			}

			fs.copyFileSync(
				filePath,
				buildsPath + tempDirPath + filePaths[fileIndex]
			);
		}
	}

	await tar.create(
		{
			gzip: true,
			file: buildsPath + "game.tar.gz",
			C: buildsPath + tempDirPath,
		},
		["."]
	);

	res.download(buildsPath + "game.tar.gz", (err) => {
		const rmSyncOptions = { recursive: true, force: true };
		fs.rmSync(buildsPath + "game.tar.gz", rmSyncOptions);
		fs.rmSync(buildsPath + tempDirPath, rmSyncOptions);
	});
};

const runReleaseDatesQuery = async (db, version_details) => {
	const timeSpanQuery = `SELECT ReleaseDate
	FROM BuildInfo
	WHERE VersionString IN
	('${version_details.curr}',
	'${version_details.update}')
	ORDER BY ReleaseDate`;

	const releaseDates = await db.all(timeSpanQuery);
	assert(releaseDates.length === 2);

	const versionStringQuery = `SELECT VersionString
	FROM BuildInfo
	WHERE ReleaseDate > '${releaseDates[0].ReleaseDate}' 
	AND ReleaseDate <= '${releaseDates[1].ReleaseDate}'`;

	const versionStrings = await db.all(versionStringQuery);
	const versionStringsArray = versionStrings.map(
		(strObj) => "'" + strObj.VersionString + "'"
	);

	if (versionStrings.length === 0) {
		console.log("No need to update");
		return null;
	}

	const gatherFilesStringQuery = `SELECT VersionString, Filepath, Action 
		FROM FileInfo f1
		WHERE VersionString IN (
			SELECT max(VersionString)
			FROM FileInfo f2
			WHERE f1.Filepath = f2.Filepath
			AND f2.VersionString IN (${versionStringsArray.join(",")})
		)`;

	const changedFiles = await db.all(gatherFilesStringQuery);
	const downloadFilePaths = {};
	const deleteFiles = [];

	changedFiles.forEach((entry) => {
		if (entry.Action === "delete") {
			deleteFiles.push(entry.Filepath);
		} else {
			const dir = entry.VersionString.replace(".", "_") + "/";
			if (downloadFilePaths[dir] === undefined) {
				downloadFilePaths[dir] = [];
			}
			downloadFilePaths[dir].push(entry.Filepath);
		}
	});

	if (!fs.existsSync(buildsPath + tempDirPath)) {
		fs.mkdirSync(buildsPath + tempDirPath);
	}

	if (deleteFiles.length) {
		fs.writeFileSync(deleteFilesPath, JSON.stringify(deleteFiles), (err) => {
			if (err) {
				console.log(
					"Error saving the temporary delete file list to JSON file."
				);
			}
		});
		return { downloadFilePaths, deleteFile: deleteFilesPath };
	}

	return { downloadFilePaths };
};

router.get("/", async (req, res) => {
	const db = await openConnection();

	if (req.query.curr) {
		const version_details = await getVersionDetails(db, req.query);
		if (!version_details.isValid) {
			return res.status(500).send("Request Parameters are missing.");
		}
		if (version_details.curr === version_details.update) {
			return res.status(200).send("Already up to date.");
		}
		// Get the release dates and get all the versions in between
		const filesToDownload = await runReleaseDatesQuery(db, version_details);
		return downloadFiles(res, filesToDownload);
	} else {
		let updateVersionQuery = "";
		if (req.query.update) {
			updateVersionQuery = `SELECT VersionString
				FROM BuildInfo
				WHERE VersionString='${req.query.update}'`;
		} else {
			updateVersionQuery = `SELECT VersionString
					FROM BuildInfo 
					ORDER BY ReleaseDate DESC`;
		}

		const result = await db.get(updateVersionQuery);
		await db.close();
		if (result) {
			const versionString = result.VersionString.replace(".", "_");
			return downloadVersion(res, versionString);
		} else {
			return res.status(500).send("Version Doesn't Exist.");
		}
	}

	res.status(200).send("No need to update.");
});

export default router;
