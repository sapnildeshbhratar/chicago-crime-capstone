
from fastapi import FastAPI, HTTPException
from api.database import get_connection, initialize_database
from api.schemas import CrimeRecord

app = FastAPI(
    title="Chicago Crime Analytics API",
    description="CRUD API for managing Chicago crime records",
    version="1.0.0"
)

# Create the API table when the application starts
@app.on_event("startup")
def startup():
    initialize_database()


# READ: Retrieve all crime records
@app.get("/crimes")
def get_all_crimes():
    conn = get_connection()

    try:
        rows = conn.execute(
            "SELECT * FROM crime_records_api ORDER BY id DESC"
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# READ: Retrieve one crime record by case number
@app.get("/crimes/{case_number}")
def get_crime(case_number: str):
    conn = get_connection()

    try:
        row = conn.execute(
            "SELECT * FROM crime_records_api WHERE case_number = ?",
            (case_number,)
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Crime record not found"
            )

        return dict(row)

    finally:
        conn.close()


# CREATE: Add a new crime record
@app.post("/crimes", status_code=201)
def create_crime(crime: CrimeRecord):
    conn = get_connection()

    try:
        data = crime.model_dump()

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))

        conn.execute(
            f"""
            INSERT INTO crime_records_api ({columns})
            VALUES ({placeholders})
            """,
            tuple(data.values())
        )

        conn.commit()

        return {
            "message": "Crime record created successfully",
            "case_number": crime.case_number
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        conn.close()


# UPDATE: Modify an existing crime record
@app.put("/crimes/{case_number}")
def update_crime(case_number: str, crime: CrimeRecord):
    conn = get_connection()

    try:
        existing = conn.execute(
            "SELECT id FROM crime_records_api WHERE case_number = ?",
            (case_number,)
        ).fetchone()

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail="Crime record not found"
            )

        if crime.case_number != case_number:
            raise HTTPException(
                status_code=400,
                detail="Case number in URL and request body must match"
            )

        data = crime.model_dump(exclude={"case_number"})

        assignments = ", ".join(
            f"{column} = ?" for column in data.keys()
        )

        conn.execute(
            f"""
            UPDATE crime_records_api
            SET {assignments}
            WHERE case_number = ?
            """,
            tuple(data.values()) + (case_number,)
        )

        conn.commit()

        return {
            "message": "Crime record updated successfully",
            "case_number": case_number
        }

    finally:
        conn.close()


# DELETE: Remove a crime record
@app.delete("/crimes/{case_number}")
def delete_crime(case_number: str):
    conn = get_connection()

    try:
        cursor = conn.execute(
            "DELETE FROM crime_records_api WHERE case_number = ?",
            (case_number,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Crime record not found"
            )

        conn.commit()

        return {
            "message": "Crime record deleted successfully",
            "case_number": case_number
        }

    finally:
        conn.close()
