import express from "express" ;
import bodyParser from "body-parser";
import buildsRoute from "./builds.mjs"
import rollbackRoute from "./rollback.mjs"
 
// Creating express object
const app = express();
 
// Defining port number
const PORT = 3000;
 
// Function to serve all static files
// inside public directory.
app.use(express.static('public'));

// parse application/json
app.use(bodyParser.json())

app.use("/builds", buildsRoute)
app.use("/rollback", rollbackRoute)
 
// Server setup
app.listen(PORT, () => {
    console.log(`Running server on PORT ${PORT}...`);
});
