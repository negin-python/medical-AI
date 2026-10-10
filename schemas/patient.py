from pydantic import BaseModel,Field,model_validator


class Patient(BaseModel):
    name:str
    age:int
    disease:str
    city:str

class PatientUpdate(BaseModel):
    name:str
    age:int
    disease:str
    city:str


class PatientPatch(BaseModel):
    name:str | None=None
    age:int |None = None
    disease:str | None = None
    city:str |None=None

class PatientPatchWrapper(BaseModel):
    success:bool
    message:str
    data:PatientPatch


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    disease: str
    city:str

class PatientResponseWrapper(BaseModel):
    success:bool
    message:str
    data:PatientResponse


class PatientListResponse(BaseModel):
    items : list[PatientResponse]
    page : int
    limit : int
    total : int
    total_pages : int
    has_next :bool
    has_previous:bool


class PatientListResponseWrapper(BaseModel):
    success:bool
    message:str
    data:PatientListResponse

class PatientFilter(BaseModel):
    disease:str |None = None
    min_age :int |None= Field (default=None,ge=0)
    max_age : int | None = Field(default=None,ge=0,le=120)
    search:str|None=None
    city:str | None=None

    @model_validator(mode="after")
    def validate_age(self):
        if(self.min_age is not None 
           and self.max_age is not None 
           and self.min_age > self.max_age):
            raise ValueError("min_age can not greater than max_age")
        return self

class DeletePatient(BaseModel):
    success:bool
    message:str
    data : None=None


class ErrorResponse(BaseModel):
    success:bool
    message:str
    data:None=None

class RestPasswordToken(BaseModel):
    token:str
    new_password:str