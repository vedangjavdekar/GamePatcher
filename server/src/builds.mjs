import express from "express"
import fs from "fs"
import multer from "multer"
import tar from "tar"
import { openConnection } from "./database.mjs";

// Settings
const runDBQueries = true;
const keepArtifacts = true;
const extractTAR = true;
const build_dir = "builds/";

const router = express.Router();
const mDiskStorage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, build_dir)
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname) //Appending extension
    }
})
const storageUpload = multer({ storage: mDiskStorage })


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

    if (query.endsWith(',')) {
        query = query.slice(0, -1);
    }

    return await db.run(query);
}

const storeBuildInfoToDatabase = async(db, VersionString, ReleaseDate) => {
    if (!runDBQueries) {
        return;
    }

    console.log("Storing Version Info...");
    return await db.run(`INSERT INTO BuildInfo(VersionString, ReleaseDate) VALUES(?,?)`, [
        VersionString,
        ReleaseDate
    ]);
}

router.post("/", storageUpload.fields([{ name: "build_manifest" }, { name: "data" }]), async (req, res) => {
    const db = await openConnection();

    console.log("processing file");
    console.log({
        body: req.body,
    })

    console.log(req.files["build_manifest"])
    console.log(req.files["data"])

    const buildManifest = fs.readFileSync(build_dir + "build_manifest.json");
    const jsonManifset = JSON.parse(buildManifest);
    console.log(jsonManifset);

    await storeBuildInfoToDatabase(db, req.body.VersionString, req.body.ReleaseDate);

    await storeManifestToDatabase(db, jsonManifset);

    db.close();

    if (extractTAR) {
        console.log("Extracting: " + build_dir + req.files['data'][0].originalname + "...")
        tar.extract({
            cwd: build_dir,
            file: build_dir + req.files['data'][0].originalname
        }).then(err => {
            if (!err) {
                console.log("Extracting Successful!");
                res.status(200).json({ message: "Success!" });
            }
            else {
                console.log(`Erros while Extracting: ${err}`);
                res.status(501).json({ message: "Something went wrong extracting the game build." });
            }
        });
    }
    else {
        res.status(200).json({ message: "Success!" });
    }
    
    if (!keepArtifacts) {
        fs.unlinkSync(req.files["build_manifest"][0].path);
        fs.unlinkSync(req.files["data"][0].path);
    }
    else {
        fs.renameSync(req.files["build_manifest"][0].path, `builds/build_manifest_${jsonManifset.version_major}_${jsonManifset.version_minor}.json`);
    }
})

export default router;