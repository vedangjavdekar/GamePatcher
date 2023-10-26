import sqlite3 from "sqlite3"
import { open } from "sqlite"

export const openConnection = async () => {
    return open({
        filename: "data/releases.db",
        driver: sqlite3.Database
    })
}