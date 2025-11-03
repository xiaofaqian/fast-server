#!/usr/bin/env python3
import asyncio

from app.services.admin_service import AdminService
from app.db.mongodb import connect_to_mongo, close_mongo_connection


async def main() -> None:
    await connect_to_mongo()
    service = AdminService()
    try:
        created = await service.init_admin()
        if created:
            print('Admin account initialized (username: nongfu).')
        else:
            print('Admin account already exists; no changes made.')
    finally:
        await close_mongo_connection()


if __name__ == '__main__':
    asyncio.run(main())
