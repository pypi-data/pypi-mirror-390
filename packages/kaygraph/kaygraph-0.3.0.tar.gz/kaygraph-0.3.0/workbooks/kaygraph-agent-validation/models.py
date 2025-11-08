"""
Pydantic models for structured data validation.
These define the schemas that LLM outputs must match.
"""

from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ============== Basic Models ==============

class TaskResult(BaseModel):
    """Basic task extraction from user input."""
    task: str = Field(description="The task description")
    completed: bool = Field(description="Whether the task is completed")
    priority: int = Field(ge=1, le=5, description="Priority level from 1-5")


class ContactInfo(BaseModel):
    """Contact information extraction."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None


# ============== Meeting Models ==============

class Meeting(BaseModel):
    """Meeting scheduling information."""
    title: str
    attendees: List[str]
    date: str = Field(description="Date in YYYY-MM-DD format")
    time: str = Field(description="Time in HH:MM format")
    duration_minutes: int = Field(ge=15, le=480)
    location: Optional[str] = None
    
    @validator('date')
    def validate_date(cls, v):
        """Ensure date is in correct format."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
        return v
    
    @validator('time')
    def validate_time(cls, v):
        """Ensure time is in correct format."""
        try:
            datetime.strptime(v, '%H:%M')
        except ValueError:
            raise ValueError('Time must be in HH:MM format')
        return v


# ============== E-commerce Models ==============

class OrderItem(BaseModel):
    """Individual item in an order."""
    product: str
    quantity: int = Field(ge=1)
    unit_price: Optional[float] = Field(ge=0, default=None)
    
    @property
    def subtotal(self) -> Optional[float]:
        """Calculate subtotal if price is available."""
        if self.unit_price is not None:
            return self.quantity * self.unit_price
        return None


class Order(BaseModel):
    """E-commerce order with multiple items."""
    items: List[OrderItem]
    customer_name: Optional[str] = None
    shipping_address: Optional[str] = None
    notes: Optional[str] = None
    
    @property
    def total_items(self) -> int:
        """Calculate total number of items."""
        return sum(item.quantity for item in self.items)
    
    @property
    def total_price(self) -> Optional[float]:
        """Calculate total price if all items have prices."""
        if all(item.unit_price is not None for item in self.items):
            return sum(item.subtotal for item in self.items)
        return None


# ============== Support Ticket Models ==============

class SupportTicket(BaseModel):
    """Customer support ticket."""
    issue_type: Literal["bug", "feature_request", "question", "complaint"]
    severity: Literal["low", "medium", "high", "critical"]
    description: str
    affected_product: Optional[str] = None
    user_email: Optional[str] = None
    
    @validator('description')
    def description_not_empty(cls, v):
        """Ensure description is not empty."""
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v


# ============== Complex Nested Models ==============

class Address(BaseModel):
    """Address component."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"


class Person(BaseModel):
    """Person with nested information."""
    first_name: str
    last_name: str
    age: Optional[int] = Field(ge=0, le=150, default=None)
    email: str
    address: Optional[Address] = None
    
    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}"


class Company(BaseModel):
    """Company with employees."""
    name: str
    industry: str
    employees: List[Person]
    headquarters: Address
    founded_year: Optional[int] = None
    
    @validator('employees')
    def at_least_one_employee(cls, v):
        """Ensure company has at least one employee."""
        if not v:
            raise ValueError('Company must have at least one employee')
        return v


# ============== Financial Models ==============

class Transaction(BaseModel):
    """Financial transaction."""
    type: Literal["credit", "debit"]
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")
    description: str
    date: str
    category: Optional[str] = None
    
    @validator('amount')
    def round_amount(cls, v):
        """Round to 2 decimal places."""
        return round(v, 2)


class BudgetCategory(BaseModel):
    """Budget category with limit."""
    name: str
    monthly_limit: float = Field(gt=0)
    current_spending: float = Field(ge=0, default=0)
    
    @property
    def remaining(self) -> float:
        """Calculate remaining budget."""
        return max(0, self.monthly_limit - self.current_spending)
    
    @property
    def is_over_budget(self) -> bool:
        """Check if over budget."""
        return self.current_spending > self.monthly_limit


class Budget(BaseModel):
    """Monthly budget with categories."""
    month: str = Field(pattern="^\\d{4}-\\d{2}$")  # YYYY-MM format
    categories: List[BudgetCategory]
    income: float = Field(gt=0)
    
    @property
    def total_limit(self) -> float:
        """Total budget limit across categories."""
        return sum(cat.monthly_limit for cat in self.categories)
    
    @property
    def total_spending(self) -> float:
        """Total current spending."""
        return sum(cat.current_spending for cat in self.categories)
    
    @property
    def savings_potential(self) -> float:
        """Potential savings if staying within budget."""
        return self.income - self.total_limit