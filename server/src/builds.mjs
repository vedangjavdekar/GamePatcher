import express from "express";
import fs from "fs";
import multer from "multer";
import tar from "tar";
import { openConnection } from "./database.mjs";
import { rollBackLastBuild } from "./rollback.mjs";

// Settings
const runDBQueries = true;
const keepArtifacts = false;
const extractTAR = true;
const build_dir = "builds/";

const router = express.Router();
const mDiskStorage = multer.diskStorage({
	destination: function (req, file, cb) {
		cb(null, build_dir);
	},
	filename: function (req, file, cb) {
		cb(null, file.originalname); //Appending extension
	},
});
const storageUpload = multer({ storage: mDiskStorage });

const storeManifestToDatabase = async (db, manifest) => {
	if (!runDBQueries) {
		return;
	}
	console.log("Storing Build Manifest...");
	let query = `INSERT INTO FileInfo(VersionMajor, VersionMinor, VersionString, Filepath, FileSize, Action) VALUES`;
	for (let i = 0; i < manifest.added_files.length; ++i) {
		query += `(${manifest.version_major}, 
            ${manifest.version_minor}, 
            "${manifest.version_str}", 
            "${manifest.added_files[i].path}", 
            ${manifest.added_files[i].size}, 
            "${manifest.added_files[i].action}"),`;
	}
	for (let i = 0; i < manifest.deleted_files.length; ++i) {
		query += `(${manifest.version_major}, 
            ${manifest.version_minor}, 
            "${manifest.version_str}",
            "${manifest.deleted_files[i].path}",
            ${manifest.deleted_files[i].size},
            "${manifest.deleted_files[i].action}"
            ),`;
	}

	if (query.endsWith(",")) {
		query = query.slice(0, -1);
	}

	return await db.run(query);
};

const storeBuildInfoToDatabase = async (db, VersionString, ReleaseDate) => {
	if (!runDBQueries) {
		return;
	}

	console.log("Storing Version Info...");
	return await db.run(
		`INSERT INTO BuildInfo(VersionString, ReleaseDate) VALUES(?,?)`,
		[VersionString, ReleaseDate]
	);
};

router.get("/", async (req, res) => {
	console.log("Getting all the builds from DB.");
	const db = await openConnection();
	const query = `SELECT * FROM BuildInfo`;

	try {
		const results = await db.all(query);
		res.status(200).json(results);
	} catch (error) {
		res.status(500).json({ error });
	}
});

/*
	async (req, res, next) => {
		console.log(req.method);
		if (req.method == "POST") {
			console.log("POST REQUEST MIDDLEWARE");
			console.log(req);

			if (auto_rollback) {
				const db = await openConnection();
				const result = await db.get(
					` SELECT * 
                FROM BuildInfo 
                ORDER BY ReleaseDate DESC
                LIMIT 1`
				);

				console.log(result);
				if (result && result.VersionString === req.body.VersionString) {
					await rollBackLastBuild(db);
				}

				await db.close();
			}
			next();
		} else {
			next();
		}
	},
 */

router.post(
	"/",
	storageUpload.fields([{ name: "build_manifest" }, { name: "data" }]),
	async (req, res) => {
		const db = await openConnection();

		console.log("processing file");
		console.log(req.body);

		console.log(req.files["build_manifest"]);
		console.log(req.files["data"]);

		const buildManifest = fs.readFileSync(build_dir + "build_manifest.json");
		const jsonManifset = JSON.parse(buildManifest);
		//console.log(jsonManifset);

		await storeBuildInfoToDatabase(
			db,
			req.body.VersionString,
			req.body.ReleaseDate
		);

		await storeManifestToDatabase(db, jsonManifset);

		await db.close();

		if (extractTAR) {
			console.log(
				"Extracting: " + build_dir + req.files["data"][0].originalname + "..."
			);
			const error = await tar.extract({
				C: build_dir,
				file: build_dir + req.files["data"][0].originalname,
			});
			if (!error) {
				console.log("Extracting Successful!");
				res.status(200).json({ message: "Success!" });
			} else {
				console.log(`Erros while Extracting: ${error}`);
				res.status(501).json({
					message: "Something went wrong extracting the game build.",
				});
			}
		} else {
			res.status(200).json({ message: "Success!" });
		}

		if (!keepArtifacts) {
			fs.unlinkSync(req.files["build_manifest"][0].path);
			fs.unlinkSync(req.files["data"][0].path);
		} else {
			fs.renameSync(
				req.files["build_manifest"][0].path,
				`builds/build_manifest_${jsonManifset.version_major}_${jsonManifset.version_minor}.json`
			);
		}
	}
);

export default router;
