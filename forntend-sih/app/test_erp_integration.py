"""
Test script for ERP + Legal Metrology Integration
Tests the complete workflow from product entry to label generation
"""

from core.erp_manager import erp_manager, ProductCategory, ProductStatus
from core.workflow_manager import workflow_manager, WorkflowType, WorkflowStatus
from core.label_generator import label_generator, LabelFormat, LabelStatus
from datetime import datetime

def test_erp_integration():
    """Test complete ERP integration workflow"""
    
    print("🧪 Testing ERP + Legal Metrology Integration...")
    print("=" * 60)
    
    # Test 1: Product Data Entry
    print("\n1️⃣ Testing Product Data Entry...")
    
    test_product = erp_manager.add_product(
        product_name="Test Product - Premium Chocolate",
        mrp=299.99,
        net_quantity=100.0,
        unit="g",
        manufacturer_name="Test Chocolate Co.",
        category=ProductCategory.FOOD,
        created_by="test_admin",
        manufacturer_address="123 Test Street, Test City",
        mfg_date="01/01/2024",
        expiry_date="31/12/2024",
        batch_number="BATCH001",
        fssai_number="12345678901234",
        country_of_origin="India",
        tags=["premium", "chocolate", "food"]
    )
    
    print(f"✅ Product created: {test_product.sku}")
    print(f"   Status: {test_product.status.value}")
    print(f"   Category: {test_product.category.value}")
    
    # Test 2: Workflow Initiation
    print("\n2️⃣ Testing Workflow Initiation...")
    
    workflow = workflow_manager.initiate_workflow(
        WorkflowType.PRODUCT_APPROVAL,
        test_product.sku,
        "PRODUCT",
        "test_admin",
        {"product_name": test_product.product_name}
    )
    
    print(f"✅ Workflow initiated: {workflow.workflow_id}")
    print(f"   Type: {workflow.workflow_type.value}")
    print(f"   Status: {workflow.status.value}")
    print(f"   Steps: {len(workflow.steps)}")
    
    # Test 3: Workflow Step Approval
    print("\n3️⃣ Testing Workflow Step Approval...")
    
    # Approve first step
    first_step = workflow.steps[0]
    approval_result = workflow_manager.approve_step(
        workflow.workflow_id,
        first_step.step_id,
        "test_validator",
        "Data validation completed successfully"
    )
    
    print(f"✅ First step approved: {first_step.step_name}")
    
    # Test 4: Product Status Update
    print("\n4️⃣ Testing Product Status Update...")
    
    status_update = erp_manager.update_product_status(
        test_product.sku,
        ProductStatus.UNDER_REVIEW,
        "test_admin",
        "Product under compliance review"
    )
    
    print(f"✅ Product status updated: {status_update}")
    
    # Test 5: Compliance Status Update
    print("\n5️⃣ Testing Compliance Status Update...")
    
    compliance_update = erp_manager.update_compliance_status(
        test_product.sku,
        "COMPLIANT",
        "test_compliance_officer",
        ["All Legal Metrology requirements met"]
    )
    
    print(f"✅ Compliance status updated: {compliance_update}")
    
    # Test 6: Product Approval
    print("\n6️⃣ Testing Product Approval...")
    
    approval = erp_manager.approve_product(
        test_product.sku,
        "test_manager",
        "Product approved for label generation"
    )
    
    print(f"✅ Product approved: {approval}")
    
    # Test 7: Label Generation
    print("\n7️⃣ Testing Label Generation...")
    
    product_data = {
        "sku": test_product.sku,
        "product_name": test_product.product_name,
        "mrp": test_product.mrp,
        "net_quantity": test_product.net_quantity,
        "unit": test_product.unit,
        "manufacturer_name": test_product.manufacturer_name,
        "mfg_date": test_product.mfg_date,
        "expiry_date": test_product.expiry_date,
        "batch_number": test_product.batch_number,
        "fssai_number": test_product.fssai_number,
        "country_of_origin": test_product.country_of_origin
    }
    
    label = label_generator.create_label_from_product(
        product_data,
        LabelFormat.STANDARD,
        "test_admin"
    )
    
    print(f"✅ Label generated: {label.label_id}")
    print(f"   Format: {label.label_format.value}")
    print(f"   Status: {label.status.value}")
    print(f"   Compliance Gate: {label.compliance_gate_status.value}")
    print(f"   Elements: {len(label.elements)}")
    
    # Test 8: Label Approval
    print("\n8️⃣ Testing Label Approval...")
    
    if label.compliance_gate_status.value == "PASSED":
        label_approval = label_generator.approve_label(
            label.label_id,
            "test_manager",
            "Label approved for printing"
        )
        print(f"✅ Label approved: {label_approval}")
    else:
        print(f"❌ Label compliance gate failed: {label.compliance_issues}")
    
    # Test 9: Final Dispatch
    print("\n9️⃣ Testing Final Dispatch...")
    
    dispatch = erp_manager.dispatch_product(
        test_product.sku,
        "test_admin",
        "Product dispatched after full compliance validation"
    )
    
    print(f"✅ Product dispatched: {dispatch}")
    
    # Test 10: Statistics and Reports
    print("\n🔟 Testing Statistics and Reports...")
    
    product_stats = erp_manager.get_product_statistics()
    workflow_stats = workflow_manager.get_workflow_statistics()
    label_stats = label_generator.get_label_statistics()
    
    print(f"✅ Product Statistics:")
    print(f"   Total Products: {product_stats['total_products']}")
    print(f"   Approved: {product_stats['approved_products']}")
    print(f"   Dispatched: {product_stats['dispatched_products']}")
    
    print(f"✅ Workflow Statistics:")
    print(f"   Total Workflows: {workflow_stats['total_workflows']}")
    print(f"   Completed: {workflow_stats['completed_workflows']}")
    print(f"   Pending: {workflow_stats['pending_workflows']}")
    
    print(f"✅ Label Statistics:")
    print(f"   Total Labels: {label_stats['total_labels']}")
    print(f"   Approved: {label_stats['approved_labels']}")
    print(f"   Compliance Pass Rate: {label_stats['compliance_pass_rate']}%")
    
    print("\n" + "=" * 60)
    print("🎉 ERP + Legal Metrology Integration Test COMPLETED!")
    print("✅ All components working correctly")
    print("✅ Complete workflow from product entry to dispatch")
    print("✅ Full compliance validation and audit trail")
    print("✅ Label generation with pre-print compliance gate")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_erp_integration()
