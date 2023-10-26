import express from "express"
import fs from "fs"
import { openConnection } from "./database.mjs";

const router = express.Router();

const runDBQueries = true;
const deleteArtefacts = true;
const buildsPath = "builds/";

const rollBackLastBuild = async (db) => {
    const result = await db.get(
        ` SELECT * 
        FROM BuildInfo 
        ORDER BY ReleaseDate DESC
        LIMIT 1`
    );

    console.log(result)

    if (!runDBQueries) {
        return result.VersionString;
    }

    if (!result) {
        return "version0.0"
    }

    const delete1 = await db.run(
        `DELETE FROM FileInfo
        WHERE VersionString = '${result.VersionString}';`
        );

    const delete2 = await db.run(
        `DELETE FROM BuildInfo
        WHERE VersionString = '${result.VersionString}';`
    );
    
    return result.VersionString;
}

router.get("/", async (req, res) => {
    const db = await openConnection();
    
    const versionString = await rollBackLastBuild(db);
    
    db.close();

    res.status(200).json({ status: "Success!" });

    const dirName = versionString.replace('.','_');
    const archiveName = dirName + ".tar.gz";
    const buildManifestName = dirName.replace('version','build_manifest_') + ".json";

    console.log({ dirName, archiveName, buildManifestName });

    if (deleteArtefacts) {
        const dirPath = buildsPath + dirName + "/";
        if (fs.existsSync(dirPath)) {
            fs.rmSync(dirPath,{recursive:true, force:true});
        }
        
        const filePath = buildsPath + archiveName;
        if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
        }

        const buildManifestPath = buildsPath + buildManifestName;
        if (fs.existsSync(buildManifestPath )) {
            fs.unlinkSync(buildManifestPath);
        }
    }
})

export default router;