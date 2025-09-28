"""
Workflow and Approval Trail Management System
Handles role-based workflows, approvals, and audit trails for Legal Metrology compliance
"""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from .json_utils import safe_json_dump, safe_json_dumps

class WorkflowStatus(Enum):
    """Workflow status enumeration"""
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ApprovalLevel(Enum):
    """Approval level enumeration"""
    LEVEL_1 = "LEVEL_1"  # Basic validation
    LEVEL_2 = "LEVEL_2"  # Technical review
    LEVEL_3 = "LEVEL_3"  # Managerial approval
    LEVEL_4 = "LEVEL_4"  # Final approval
    ADMIN = "ADMIN"      # Administrative override

class WorkflowType(Enum):
    """Workflow type enumeration"""
    PRODUCT_APPROVAL = "PRODUCT_APPROVAL"
    COMPLIANCE_REVIEW = "COMPLIANCE_REVIEW"
    LABEL_GENERATION = "LABEL_GENERATION"
    DISPATCH_APPROVAL = "DISPATCH_APPROVAL"
    REGULATORY_UPDATE = "REGULATORY_UPDATE"
    SYSTEM_CONFIGURATION = "SYSTEM_CONFIGURATION"

@dataclass
class WorkflowStep:
    """Individual workflow step"""
    step_id: str
    step_name: str
    required_role: str
    approval_level: ApprovalLevel
    status: WorkflowStatus
    assigned_to: Optional[str] = None
    started_date: Optional[str] = None
    completed_date: Optional[str] = None
    comments: Optional[str] = None
    attachments: List[str] = None
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []

@dataclass
class WorkflowInstance:
    """Workflow instance for a specific process"""
    workflow_id: str
    workflow_type: WorkflowType
    entity_id: str  # SKU, complaint_id, etc.
    entity_type: str  # "PRODUCT", "COMPLAINT", "RULE", etc.
    status: WorkflowStatus
    initiated_by: str
    initiated_date: str
    completed_date: Optional[str] = None
    current_step: Optional[str] = None
    steps: List[WorkflowStep] = None
    metadata: Dict[str, Any] = None
    notes: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        if self.metadata is None:
            self.metadata = {}
        if self.notes is None:
            self.notes = []

class WorkflowManager:
    """Manages workflows, approvals, and audit trails"""
    
    def __init__(self):
        self.workflows_file = Path("app/data/workflows.json")
        self.workflows_file.parent.mkdir(parents=True, exist_ok=True)
        self.workflows = self._load_workflows()
        
        # Define workflow templates
        self.workflow_templates = self._define_workflow_templates()
    
    def _load_workflows(self) -> List[WorkflowInstance]:
        """Load workflows from file"""
        if not self.workflows_file.exists():
            return []
        
        try:
            with open(self.workflows_file, 'r') as f:
                data = json.load(f)
                workflows = []
                for item in data:
                    # Convert enum values back to enum objects
                    item['workflow_type'] = WorkflowType(item['workflow_type'])
                    item['status'] = WorkflowStatus(item['status'])
                    
                    # Convert steps
                    steps = []
                    for step_data in item.get('steps', []):
                        step_data['approval_level'] = ApprovalLevel(step_data['approval_level'])
                        step_data['status'] = WorkflowStatus(step_data['status'])
                        steps.append(WorkflowStep(**step_data))
                    item['steps'] = steps
                    
                    workflows.append(WorkflowInstance(**item))
                return workflows
        except Exception as e:
            print(f"Error loading workflows: {e}")
            return []
    
    def _save_workflows(self):
        """Save workflows to file"""
        try:
            # Convert workflows to dictionaries
            data = []
            for workflow in self.workflows:
                workflow_dict = asdict(workflow)
                # Convert enums to string values
                workflow_dict['workflow_type'] = workflow.workflow_type.value
                workflow_dict['status'] = workflow.status.value
                
                # Convert steps
                steps_data = []
                for step in workflow.steps:
                    step_dict = asdict(step)
                    step_dict['approval_level'] = step.approval_level.value
                    step_dict['status'] = step.status.value
                    steps_data.append(step_dict)
                workflow_dict['steps'] = steps_data
                
                data.append(workflow_dict)
            
            with open(self.workflows_file, 'w') as f:
                safe_json_dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving workflows: {e}")
    
    def _define_workflow_templates(self) -> Dict[WorkflowType, List[Dict]]:
        """Define workflow templates for different types"""
        return {
            WorkflowType.PRODUCT_APPROVAL: [
                {
                    "step_name": "Data Validation",
                    "required_role": "VALIDATOR",
                    "approval_level": ApprovalLevel.LEVEL_1,
                    "description": "Validate product data completeness and accuracy"
                },
                {
                    "step_name": "Compliance Check",
                    "required_role": "COMPLIANCE_OFFICER",
                    "approval_level": ApprovalLevel.LEVEL_2,
                    "description": "Verify Legal Metrology compliance"
                },
                {
                    "step_name": "Manager Approval",
                    "required_role": "MANAGER",
                    "approval_level": ApprovalLevel.LEVEL_3,
                    "description": "Manager review and approval"
                },
                {
                    "step_name": "Final Approval",
                    "required_role": "ADMIN",
                    "approval_level": ApprovalLevel.LEVEL_4,
                    "description": "Final administrative approval"
                }
            ],
            WorkflowType.COMPLIANCE_REVIEW: [
                {
                    "step_name": "Issue Analysis",
                    "required_role": "COMPLIANCE_OFFICER",
                    "approval_level": ApprovalLevel.LEVEL_2,
                    "description": "Analyze compliance issues and violations"
                },
                {
                    "step_name": "Resolution Planning",
                    "required_role": "MANAGER",
                    "approval_level": ApprovalLevel.LEVEL_3,
                    "description": "Plan resolution strategy"
                },
                {
                    "step_name": "Implementation Approval",
                    "required_role": "ADMIN",
                    "approval_level": ApprovalLevel.LEVEL_4,
                    "description": "Approve implementation plan"
                }
            ],
            WorkflowType.LABEL_GENERATION: [
                {
                    "step_name": "Label Design",
                    "required_role": "DESIGNER",
                    "approval_level": ApprovalLevel.LEVEL_1,
                    "description": "Create compliant label design"
                },
                {
                    "step_name": "Compliance Review",
                    "required_role": "COMPLIANCE_OFFICER",
                    "approval_level": ApprovalLevel.LEVEL_2,
                    "description": "Review label compliance"
                },
                {
                    "step_name": "Pre-Print Approval",
                    "required_role": "MANAGER",
                    "approval_level": ApprovalLevel.LEVEL_3,
                    "description": "Approve label before printing"
                }
            ]
        }
    
    def generate_workflow_id(self, workflow_type: WorkflowType) -> str:
        """Generate unique workflow ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        type_prefix = workflow_type.value[:3].upper()
        count = len([w for w in self.workflows if w.workflow_id.startswith(f"{type_prefix}-{timestamp}")])
        return f"{type_prefix}-{timestamp}-{count:03d}"
    
    def initiate_workflow(self, workflow_type: WorkflowType, entity_id: str, 
                         entity_type: str, initiated_by: str, metadata: Dict[str, Any] = None) -> WorkflowInstance:
        """Initiate a new workflow"""
        
        workflow_id = self.generate_workflow_id(workflow_type)
        
        # Create workflow steps from template
        steps = []
        template = self.workflow_templates.get(workflow_type, [])
        
        for i, step_template in enumerate(template):
            step = WorkflowStep(
                step_id=f"{workflow_id}-STEP-{i+1:02d}",
                step_name=step_template["step_name"],
                required_role=step_template["required_role"],
                approval_level=step_template["approval_level"],
                status=WorkflowStatus.INITIATED if i == 0 else WorkflowStatus.INITIATED
            )
            steps.append(step)
        
        workflow = WorkflowInstance(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            entity_id=entity_id,
            entity_type=entity_type,
            status=WorkflowStatus.INITIATED,
            initiated_by=initiated_by,
            initiated_date=datetime.now().isoformat(),
            current_step=steps[0].step_id if steps else None,
            steps=steps,
            metadata=metadata or {}
        )
        
        # Start the first step
        if steps:
            steps[0].status = WorkflowStatus.IN_PROGRESS
            steps[0].started_date = datetime.now().isoformat()
        
        self.workflows.append(workflow)
        self._save_workflows()
        
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowInstance]:
        """Get workflow by ID"""
        for workflow in self.workflows:
            if workflow.workflow_id == workflow_id:
                return workflow
        return None
    
    def get_workflows_by_entity(self, entity_id: str, entity_type: str = None) -> List[WorkflowInstance]:
        """Get workflows by entity"""
        workflows = []
        for workflow in self.workflows:
            if workflow.entity_id == entity_id:
                if entity_type is None or workflow.entity_type == entity_type:
                    workflows.append(workflow)
        return workflows
    
    def get_pending_workflows(self, user_role: str) -> List[WorkflowInstance]:
        """Get workflows pending action by user role"""
        pending = []
        for workflow in self.workflows:
            if workflow.status in [WorkflowStatus.IN_PROGRESS, WorkflowStatus.PENDING_APPROVAL]:
                current_step = next((step for step in workflow.steps if step.step_id == workflow.current_step), None)
                if current_step and current_step.required_role == user_role and current_step.status == WorkflowStatus.IN_PROGRESS:
                    pending.append(workflow)
        return pending
    
    def approve_step(self, workflow_id: str, step_id: str, approved_by: str, 
                    comments: str = None, attachments: List[str] = None) -> bool:
        """Approve a workflow step"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        step = next((s for s in workflow.steps if s.step_id == step_id), None)
        if not step:
            return False
        
        # Update step
        step.status = WorkflowStatus.APPROVED
        step.completed_date = datetime.now().isoformat()
        step.comments = comments
        if attachments:
            step.attachments.extend(attachments)
        
        # Add note
        workflow.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": approved_by,
            "note": f"Step '{step.step_name}' approved by {approved_by}"
        })
        
        # Move to next step or complete workflow
        self._advance_workflow(workflow, approved_by)
        
        return True
    
    def reject_step(self, workflow_id: str, step_id: str, rejected_by: str, 
                   reason: str) -> bool:
        """Reject a workflow step"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        step = next((s for s in workflow.steps if s.step_id == step_id), None)
        if not step:
            return False
        
        # Update step
        step.status = WorkflowStatus.REJECTED
        step.completed_date = datetime.now().isoformat()
        step.comments = f"REJECTED: {reason}"
        
        # Update workflow status
        workflow.status = WorkflowStatus.REJECTED
        workflow.completed_date = datetime.now().isoformat()
        
        # Add note
        workflow.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": rejected_by,
            "note": f"Step '{step.step_name}' rejected by {rejected_by}: {reason}"
        })
        
        self._save_workflows()
        return True
    
    def assign_step(self, workflow_id: str, step_id: str, assigned_to: str, assigned_by: str) -> bool:
        """Assign a workflow step to a user"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        step = next((s for s in workflow.steps if s.step_id == step_id), None)
        if not step:
            return False
        
        step.assigned_to = assigned_to
        step.status = WorkflowStatus.PENDING_APPROVAL
        
        # Add note
        workflow.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": assigned_by,
            "note": f"Step '{step.step_name}' assigned to {assigned_to}"
        })
        
        self._save_workflows()
        return True
    
    def _advance_workflow(self, workflow: WorkflowInstance, updated_by: str):
        """Advance workflow to next step"""
        current_step_index = -1
        for i, step in enumerate(workflow.steps):
            if step.step_id == workflow.current_step:
                current_step_index = i
                break
        
        if current_step_index == -1:
            return
        
        # Check if there's a next step
        next_step_index = current_step_index + 1
        if next_step_index < len(workflow.steps):
            # Move to next step
            next_step = workflow.steps[next_step_index]
            workflow.current_step = next_step.step_id
            next_step.status = WorkflowStatus.IN_PROGRESS
            next_step.started_date = datetime.now().isoformat()
            workflow.status = WorkflowStatus.IN_PROGRESS
        else:
            # Workflow completed
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_date = datetime.now().isoformat()
            workflow.current_step = None
            
            # Add completion note
            workflow.notes.append({
                "timestamp": datetime.now().isoformat(),
                "user": updated_by,
                "note": "Workflow completed successfully"
            })
        
        self._save_workflows()
    
    def cancel_workflow(self, workflow_id: str, cancelled_by: str, reason: str) -> bool:
        """Cancel a workflow"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        workflow.status = WorkflowStatus.CANCELLED
        workflow.completed_date = datetime.now().isoformat()
        
        # Add cancellation note
        workflow.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": cancelled_by,
            "note": f"Workflow cancelled: {reason}"
        })
        
        self._save_workflows()
        return True
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        total = len(self.workflows)
        
        if total == 0:
            return {
                "total_workflows": 0,
                "by_status": {},
                "by_type": {},
                "avg_completion_time_hours": 0,
                "pending_workflows": 0,
                "completed_workflows": 0
            }
        
        # Count by status
        status_counts = {}
        for status in WorkflowStatus:
            status_counts[status.value] = len([w for w in self.workflows if w.status == status])
        
        # Count by type
        type_counts = {}
        for workflow_type in WorkflowType:
            type_counts[workflow_type.value] = len([w for w in self.workflows if w.workflow_type == workflow_type])
        
        # Calculate average completion time
        completed_workflows = [w for w in self.workflows if w.completed_date]
        if completed_workflows:
            total_hours = 0
            for workflow in completed_workflows:
                start_date = datetime.fromisoformat(workflow.initiated_date)
                end_date = datetime.fromisoformat(workflow.completed_date)
                hours = (end_date - start_date).total_seconds() / 3600
                total_hours += hours
            avg_completion_time = total_hours / len(completed_workflows)
        else:
            avg_completion_time = 0
        
        return {
            "total_workflows": total,
            "by_status": status_counts,
            "by_type": type_counts,
            "avg_completion_time_hours": round(avg_completion_time, 2),
            "pending_workflows": status_counts.get("IN_PROGRESS", 0) + status_counts.get("PENDING_APPROVAL", 0),
            "completed_workflows": status_counts.get("COMPLETED", 0)
        }

# Global workflow manager instance
workflow_manager = WorkflowManager()
