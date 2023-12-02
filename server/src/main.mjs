import express from "express";
import buildsRoute from "./builds.mjs";
import rollbackRoute from "./rollback.mjs";
import downloadRoute from "./download.mjs";

// Creating express object
const app = express();

// Defining port number
const PORT = 3000;

// parse application/json
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use("/builds", buildsRoute);
app.use("/rollback", rollbackRoute);
app.use("/download", downloadRoute);

// Server setup
app.listen(PORT, () => {
	console.log(`Running server on PORT ${PORT}...`);
});
