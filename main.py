import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import ContactMessage, NewsletterSubscriber, PortfolioVisit

app = FastAPI(title="Mechatronics Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Static portfolio content (served by API) ----------
class Link(BaseModel):
    label: str
    href: str

class Tech(BaseModel):
    name: str
    level: str

class ShowcaseProject(BaseModel):
    title: str
    tagline: str
    description: str
    tech: List[str]
    highlights: List[str]
    repo: Optional[str] = None
    demo: Optional[str] = None
    images: List[str] = []


PROFILE = {
    "name": "Mechatronics Student",
    "university": "Dedan Kimathi University of Technology (DeKUT)",
    "location": "Nyeri, Kenya",
    "tagline": "Building robots and smart systems that bridge hardware and software.",
    "avatar": "/avatar.png",
    "links": [
        {"label": "GitHub", "href": "https://github.com/"},
        {"label": "LinkedIn", "href": "https://linkedin.com/"},
        {"label": "Email", "href": "mailto:student@example.com"},
    ],
}

SKILLS = [
    {"name": "Control Systems", "level": "Advanced"},
    {"name": "Embedded C/C++", "level": "Advanced"},
    {"name": "Python (Robotics)", "level": "Advanced"},
    {"name": "ROS / ROS2", "level": "Intermediate"},
    {"name": "Computer Vision (OpenCV)", "level": "Intermediate"},
    {"name": "PCB Design (KiCad)", "level": "Intermediate"},
    {"name": "3D CAD (Fusion 360)", "level": "Intermediate"},
    {"name": "IoT (ESP32, MQTT)", "level": "Advanced"},
]

PROJECTS: List[ShowcaseProject] = [
    ShowcaseProject(
        title="Vision-Guided Line Follower",
        tagline="A high-speed line follower with PID and camera correction",
        description=(
            "Designed and built a differential drive robot with an ESP32, optical sensor array, "
            "and onboard camera for corner detection. Implemented PID control and Kalman filtering "
            "for smooth tracking and anti-overshoot behavior."
        ),
        tech=["ESP32", "PID", "OpenCV", "Python", "3D Printed Chassis"],
        highlights=[
            "100+ samples/sec sensor fusion",
            "On-the-fly PID tuning via BLE",
            "Real-time telemetry dashboard",
        ],
        repo="https://github.com/",
        demo="https://youtu.be/",
        images=["/projects/line-follower-1.jpg", "/projects/line-follower-2.jpg"],
    ),
    ShowcaseProject(
        title="Robotic Arm with Inverse Kinematics",
        tagline="5-DOF desktop arm with web-based control",
        description=(
            "Built a 3D-printed 5-DOF arm driven by stepper motors, controlled with a Raspberry Pi. "
            "Implemented inverse kinematics in Python and exposed a web UI for trajectory planning."
        ),
        tech=["Raspberry Pi", "Python", "Flask/React", "Stepper Drivers", "IK"],
        highlights=[
            "Configurable workspace limits",
            "Saved motion profiles",
            "Camera-based calibration",
        ],
        repo="https://github.com/",
        demo="https://youtu.be/",
        images=["/projects/arm-1.jpg", "/projects/arm-2.jpg"],
    ),
]

TIMELINE = [
    {
        "year": "2025",
        "items": [
            "Final year at DeKUT focusing on autonomous systems",
            "Research: Low-cost visual odometry for indoor robots",
        ],
    },
    {
        "year": "2024",
        "items": [
            "Internship: Industrial automation (PLC, SCADA)",
            "Robotics club lead: organized 3 hackathons",
        ],
    },
]


@app.get("/")
def root():
    return {
        "name": PROFILE["name"],
        "message": "Mechatronics Portfolio API running",
    }


@app.get("/profile")
def get_profile():
    return PROFILE


@app.get("/skills")
def get_skills():
    return SKILLS


@app.get("/projects")
def get_projects():
    return [p.model_dump() for p in PROJECTS]


@app.get("/timeline")
def get_timeline():
    return TIMELINE


# ---------- Persisted endpoints (MongoDB) ----------
@app.post("/contact")
def submit_contact(payload: ContactMessage):
    try:
        doc_id = create_document("contactmessage", payload)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contact")
def list_contacts(limit: int = 20):
    try:
        items = get_documents("contactmessage", limit=limit)
        # Convert ObjectId to string for safety
        for it in items:
            if "_id" in it:
                it["_id"] = str(it["_id"])
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/subscribe")
def subscribe(payload: NewsletterSubscriber):
    try:
        doc_id = create_document("newslettersubscriber", payload)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/visit")
def log_visit(payload: PortfolioVisit):
    try:
        doc_id = create_document("portfoliovisit", payload)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health/database test remains
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
