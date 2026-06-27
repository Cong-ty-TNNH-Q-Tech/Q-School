"""
Q-School AI — Seed Data Script
Chạy sau khi alembic upgrade head để seed thêm dữ liệu demo.

Usage:
    cd backend
    python scripts/seed_demo_data.py

NOTE: Migration 0001 đã seed dữ liệu cơ bản:
  - 3 Plans: Free, Pro, Enterprise
  - 3 AI Personas: Raina, Tutor, StudyBot
  Script này thêm dữ liệu demo cho development/testing.
"""
import asyncio
import sys
import os

# Thêm backend vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine


async def seed_admin_user():
    """Tạo Admin user mặc định nếu chưa tồn tại."""
    from pwdlib import PasswordHash
    from pwdlib.hashers.bcrypt import BcryptHasher
    pwd_hasher = PasswordHash((BcryptHasher(),))
    admin_password = pwd_hasher.hash("admin123")

    async with engine.begin() as conn:
        # Check if admin exists
        result = await conn.execute(
            text("SELECT id FROM users WHERE username = 'admin'")
        )
        if result.first():
            print("  [SKIP] Admin user already exists")
            return

        # Create admin user
        await conn.execute(text("""
            INSERT INTO users (username, email, password_hash, role, is_active)
            VALUES ('admin', 'admin@qschool.ai', :password, 'admin', true)
        """), {"password": admin_password})

        # Create admin profile
        await conn.execute(text("""
            INSERT INTO profiles (user_id, full_name, bio)
            SELECT id, 'System Administrator', 'Q-School AI System Admin'
            FROM users WHERE username = 'admin'
        """))

        print("  [OK] Admin user created (admin / admin123)")


async def seed_demo_teacher():
    """Tạo Teacher demo nếu chưa tồn tại."""
    from pwdlib import PasswordHash
    from pwdlib.hashers.bcrypt import BcryptHasher
    pwd_hasher = PasswordHash((BcryptHasher(),))
    teacher_password = pwd_hasher.hash("teacher123")

    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT id FROM users WHERE username = 'teacher_demo'")
        )
        if result.first():
            print("  [SKIP] Demo teacher already exists")
            return

        await conn.execute(text("""
            INSERT INTO users (username, email, password_hash, role, is_active)
            VALUES ('teacher_demo', 'teacher@qschool.ai', :password, 'teacher', true)
        """), {"password": teacher_password})

        await conn.execute(text("""
            INSERT INTO profiles (user_id, full_name, school_name, bio)
            SELECT id, 'Nguyen Van A', 'THPT ABC', 'Demo teacher account'
            FROM users WHERE username = 'teacher_demo'
        """))

        print("  [OK] Demo teacher created (teacher_demo / teacher123)")


async def seed_demo_student():
    """Tạo Student demo nếu chưa tồn tại."""
    from pwdlib import PasswordHash
    from pwdlib.hashers.bcrypt import BcryptHasher
    pwd_hasher = PasswordHash((BcryptHasher(),))
    student_password = pwd_hasher.hash("student123")

    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT id FROM users WHERE username = 'student_demo'")
        )
        if result.first():
            print("  [SKIP] Demo student already exists")
            return

        await conn.execute(text("""
            INSERT INTO users (username, email, password_hash, role, is_active)
            VALUES ('student_demo', 'student@qschool.ai', :password, 'student', true)
        """), {"password": student_password})

        await conn.execute(text("""
            INSERT INTO profiles (user_id, full_name, school_name, bio, points)
            SELECT id, 'Tran Thi B', 'THPT ABC', 'Demo student account', 0
            FROM users WHERE username = 'student_demo'
        """))

        print("  [OK] Demo student created (student_demo / student123)")


async def verify_seed_data():
    """Kiểm tra dữ liệu seed từ migration 0001."""
    async with engine.connect() as conn:
        # Check Plans
        result = await conn.execute(text("SELECT name, price FROM plans WHERE is_active = true ORDER BY price"))
        plans = result.fetchall()
        print(f"\n  Plans seeded: {len(plans)}")
        for plan in plans:
            print(f"    - {plan[0]}: {plan[1]:,} VND/month")

        # Check AI Personas
        result = await conn.execute(text("SELECT persona_name, version FROM ai_prompts"))
        personas = result.fetchall()
        print(f"\n  AI Personas seeded: {len(personas)}")
        for persona in personas:
            print(f"    - {persona[0]} ({persona[1]})")

        # Check Users
        result = await conn.execute(text("SELECT username, role FROM users ORDER BY created_at"))
        users = result.fetchall()
        print(f"\n  Users: {len(users)}")
        for user in users:
            print(f"    - {user[0]} ({user[1]})")


async def main():
    print("=" * 50)
    print("Q-School AI — Seed Demo Data")
    print("=" * 50)

    print("\n[1/3] Seeding admin user...")
    await seed_admin_user()

    print("\n[2/3] Seeding demo teacher...")
    await seed_demo_teacher()

    print("\n[3/3] Seeding demo student...")
    await seed_demo_student()

    print("\n[Verify] Checking all seed data...")
    await verify_seed_data()

    await engine.dispose()
    print("\n" + "=" * 50)
    print("Seed complete!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
