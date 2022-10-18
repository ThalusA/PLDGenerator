from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from datetime import date as date_type


class LocaleDictionary(BaseModel):
    title: str
    subtitle: str
    document_description: str
    description: str
    locale: str
    due_date: str
    end_date: str
    authors: str
    updated_date: str
    model_version: str
    stats: str
    man_days_distribution: str
    total_man_days: str
    revision_table: str
    date: str
    version: str
    sections: str
    comment: str
    table_of_content: str
    organigram: str
    deliverable_map: str
    user_stories: str
    as_user: str
    user_want: str
    definition_of_done: str
    assignation: str
    estimated_duration: str
    man_days: str
    hours: str
    status: str
    comments: str
    advancement_report: str
    to_do: str
    wip: str
    done: str
    abandoned: str
    project_log_document: str
    page: str
    of: str


class Version(BaseModel):
    version: str = Field(regex=r"^\d+\.\d+\.\d+$")
    date: date_type = Field(description="Release date of this version")
    authors: List[str] = Field(default_factory=list, description="Authors of this version", min_items=1)
    sections: str = Field(description="Which sections have been modified", min_length=1)
    comment: str = Field(description="Comment about this version", min_length=1)


class Status(str, Enum):
    to_do = "To do"
    wip = "WIP"
    done = "Done"
    abandoned = "Abandoned"

    def to_priority(self) -> int:
        if self.name == Status.to_do:
            return 2
        elif self.name == Status.wip:
            return 3
        elif self.name == Status.done:
            return 4
        elif self.name == Status.abandoned:
            return 1
        else:
            return 0

    def translate(self, locale: LocaleDictionary) -> str:
        if self == Status.to_do:
            return locale.to_do
        elif self == Status.wip:
            return locale.wip
        elif self == Status.done:
            return locale.done
        elif self == Status.abandoned:
            return locale.abandoned
        else:
            return ""


class UserStory(BaseModel):
    type: str = Field("user_story", const=True)
    name: str = Field(description="Name of the user story", min_length=1)
    user: str = Field(description="User that do the action of user story")
    action: str = Field(description="Action done by the user")
    description: Optional[str] = Field(None, description="Detailed description of the user")
    definitions_of_done: List[str] = Field(default_factory=list, min_items=1,
                                           description="List of definition of done (list of goal) that must be done to "
                                                       "complete the user story")
    estimated_duration: float = Field(description="Number of estimated man day (8 hours)",
                                      multiple_of=0.5)
    due_date: Optional[date_type] = Field(None, description="User story due date")
    end_date: Optional[date_type] = Field(None, description="Date when the user story was marked as Done")
    status: Status = Field(Status.to_do, description="User story work status")
    assignments: List[str] = Field(default_factory=list,
                                   description="List of person assigned to work on this user story")
    comments: Optional[Union[List[str], str]] = Field(None, description="Comment about the user story")


class Subset(BaseModel):
    type: str = Field("subset", const=True)
    name: str = Field(min_length=1)
    description: Optional[str] = Field(None)
    user_stories: List[UserStory] = Field(default_factory=list, min_items=1)


class Deliverable(BaseModel):
    type: str = Field("deliverable", const=True)
    name: str = Field(min_length=1)
    description: Optional[str] = Field(None)
    subsets: List[Subset] = Field(default_factory=list, description="Subset that groups many user story",
                                  min_items=1)


class Locale(str, Enum):
    french = "fr_FR"


class PLDSchema(BaseModel):
    locale: Locale = Field(description="Locale of the PLD")
    title: str = Field(description="Main title on document title page", min_length=1)
    subtitle: Optional[str] = Field(None, description="Subtitle on document title page", min_length=1)
    description: Optional[str] = Field(None, description="Description of document", min_length=1)
    authors: List[str] = Field(default_factory=list, description="List of document authors", min_items=1)
    versions: List[Version] = Field(default_factory=list)
    deliverables: List[Deliverable] = Field(default_factory=list, description="Project deliverable")
