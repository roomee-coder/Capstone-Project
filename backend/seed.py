import random
import string
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)


def random_title():
    return " ".join(
        "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
        for _ in range(random.randint(2, 4))
    )


def seed(count, project_id):
    db = SessionLocal()
    priorities = ["low", "medium", "high"]
    statuses = ["pending", "in_progress", "completed"]

    for _ in range(count):
        task = models.Task(
            title=random_title(),
            priority=random.choice(priorities),
            due_date="next friday",
            status=random.choice(statuses),
            project_id=project_id,
        )
        db.add(task)

    db.commit()
    db.close()
    print(f"Seeded {count} tasks under project_id={project_id}")


if __name__ == "__main__":
    seed(10, project_id=1)
    seed(500, project_id=1)
    seed(3000, project_id=1)