# 🚨 CRITICAL FORMAT FIXES REQUIRED

## **MAJOR ISSUE DISCOVERED:**

### **❌ Current Training Data Format (WRONG):**
```json
{"tool_call":{"id":"call_123","name":"verify_user","arguments":{"maiden_name":"Kaya","phone_last4":"7788"}}}
{"tool_call":{"id":"call_456","name":"get_user_info","arguments":{"user_id":"1101"}}}
```

### **✅ Backend Expected Format (CORRECT):**
```json
{"tool_call":{"id":"call_123","name":"verify_user","arguments":{"maiden_name":"Kaya","msisdn":"905551234567"}}}
{"tool_call":{"id":"call_456","name":"get_user_info","arguments":{"customer_id":"1101"}}}
```

## **🔧 REQUIRED FIXES:**

### **1. verify_user Tool:**
- **WRONG**: `"phone_last4": "7788"`
- **CORRECT**: `"msisdn": "905551234567"` (full phone number)

### **2. All Other Tools:**
- **WRONG**: `"user_id": "1101"`
- **CORRECT**: `"customer_id": "1101"`

### **3. Backend Tool Schema (from registry.py):**
```python
"verify_user": {
    "required": ["maiden_name", "msisdn"]  # NOT phone_last4
},
"get_user_info": {
    "required": ["customer_id"]  # NOT user_id
},
"check_device_registration": {
    "required": ["customer_id"]  # NOT user_id
}
# ... all tools use "customer_id", not "user_id"
```

## **🚨 TRAINING DATA IS INCOMPATIBLE!**

**The model will be trained on wrong argument names and won't work with the backend!**

## **💊 IMMEDIATE FIXES NEEDED:**

### **Fix 1: Update ChatGPT Prompts**
- Change all `user_id` → `customer_id`
- Change `phone_last4` → `msisdn` (full number)

### **Fix 2: Update Existing Training Data**
- Run conversion script on all generated data
- Fix argument name mismatches

### **Fix 3: Update Dataset Generators**
- All `dataset_step*.py` files need fixing
- `MasterDatasetGenerator` needs correction

### **Fix 4: Backend Verification Flow**
- Backend returns `customer_id` after verification
- All subsequent tools must use this `customer_id`

## **🎯 CORRECT WORKFLOW:**
```
1. verify_user(maiden_name="X", msisdn="905551234567")
   → returns: {"success": true, "customer_id": "12345"}

2. get_user_info(customer_id="12345")
   → uses customer_id from step 1

3. ALL tools use customer_id, NOT user_id
```

**THIS MUST BE FIXED BEFORE TRAINING OR THE MODEL WON'T WORK!** 🚨
