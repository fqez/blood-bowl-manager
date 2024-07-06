from typing import List, Union

from beanie import PydanticObjectId

from models.student import Student
from models.team.character import Character
from models.team.perk import Perk
from models.team.team import Team
from models.user.admin import Admin

admin_collection = Admin
student_collection = Student
perk_collection = Perk
team_collection = Team


async def add_admin(new_admin: Admin) -> Admin:
    admin = await new_admin.create()
    return admin


async def retrieve_perks() -> List[Perk]:
    perks = await perk_collection.all().to_list()
    return perks


async def retrieve_teams() -> List[Team]:
    teams = await team_collection.all().to_list()
    return teams


async def retrieve_team(id: str) -> Team:
    team = await team_collection.get(id)
    if team:
        return team


async def update_character_data(
    team: Team, character: Character, data: dict
) -> Union[bool, Team]:
    des_body = {k: v for k, v in data.items() if v is not None}
    update_query = {"$set": {field: value for field, value in des_body.items()}}
    if team:
        await team.update(update_query)
        return team
    return False


async def add_team(new_team: Team) -> Team:
    team = await new_team.create()
    return team


async def retrieve_students() -> List[Student]:
    students = await student_collection.all().to_list()
    return students


async def add_student(new_student: Student) -> Student:
    student = await new_student.create()
    return student


async def retrieve_student(id: PydanticObjectId) -> Student:
    student = await student_collection.get(id)
    if student:
        return student


async def delete_student(id: PydanticObjectId) -> bool:
    student = await student_collection.get(id)
    if student:
        await student.delete()
        return True


async def update_student_data(id: PydanticObjectId, data: dict) -> Union[bool, Student]:
    des_body = {k: v for k, v in data.items() if v is not None}
    update_query = {"$set": {field: value for field, value in des_body.items()}}
    student = await student_collection.get(id)
    if student:
        await student.update(update_query)
        return student
    return False
