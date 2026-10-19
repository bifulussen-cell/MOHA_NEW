import requests
import sys
import json
import base64
from datetime import datetime, timedelta
import time

class PetCompanionAPITester:
    def __init__(self, base_url="https://pethealthai-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.pet_id = None
        self.listing_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)
        
        if files:
            # Remove Content-Type for file uploads
            test_headers.pop('Content-Type', None)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, headers=test_headers)
                else:
                    response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health check"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root Endpoint", "GET", "", 200)

    def test_user_registration(self):
        """Test user registration"""
        test_user_data = {
            "email": f"test_user_{int(time.time())}@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response.get('user', {})
            print(f"   Registered user: {self.user_data.get('email')}")
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        if not self.user_data:
            print("❌ No user data available for login test")
            return False
            
        login_data = {
            "email": self.user_data.get('email'),
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_pet_creation(self):
        """Test pet creation"""
        pet_data = {
            "name": "Buddy",
            "species": "dog",
            "breed": "Golden Retriever",
            "age": 3,
            "weight": 25.5,
            "gender": "male",
            "color": "golden",
            "medical_notes": "Healthy and active"
        }
        
        success, response = self.run_test(
            "Pet Creation",
            "POST",
            "pets",
            200,
            data=pet_data
        )
        
        if success and 'id' in response:
            self.pet_id = response['id']
            print(f"   Created pet: {response.get('name')} (ID: {self.pet_id})")
            return True
        return False

    def test_get_user_pets(self):
        """Test getting user's pets"""
        return self.run_test("Get User Pets", "GET", "pets", 200)

    def test_get_specific_pet(self):
        """Test getting specific pet by ID"""
        if not self.pet_id:
            print("❌ No pet ID available for specific pet test")
            return False
            
        return self.run_test(
            "Get Specific Pet",
            "GET",
            f"pets/{self.pet_id}",
            200
        )

    def test_health_analysis(self):
        """Test AI health analysis with sample image"""
        if not self.pet_id:
            print("❌ No pet ID available for health analysis test")
            return False
        
        # Create a simple test image (1x1 pixel PNG)
        test_image_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGA4nEKtAAAAABJRU5ErkJggg=="
        )
        
        files = {
            'file': ('test_pet.png', test_image_data, 'image/png')
        }
        
        success, response = self.run_test(
            "Health Analysis",
            "POST",
            f"pets/{self.pet_id}/health-analysis",
            200,
            files=files
        )
        
        if success:
            print("   AI Health Analysis completed successfully")
            return True
        return False

    def test_get_health_analyses(self):
        """Test getting pet health analyses"""
        if not self.pet_id:
            print("❌ No pet ID available for health analyses test")
            return False
            
        return self.run_test(
            "Get Health Analyses",
            "GET",
            f"pets/{self.pet_id}/health-analyses",
            200
        )

    def test_daily_tip(self):
        """Test getting daily tip for pet"""
        if not self.pet_id:
            print("❌ No pet ID available for daily tip test")
            return False
            
        success, response = self.run_test(
            "Get Daily Tip",
            "GET",
            f"pets/{self.pet_id}/daily-tip",
            200
        )
        
        if success:
            print("   Daily tip generated successfully")
            return True
        return False

    def test_recovery_stories(self):
        """Test getting recovery stories"""
        return self.run_test("Get Recovery Stories", "GET", "recovery-stories", 200)

    def test_social_post_creation(self):
        """Test creating a social post"""
        if not self.pet_id:
            print("❌ No pet ID available for social post test")
            return False
            
        post_data = {
            "pet_id": self.pet_id,
            "content": "My pet is doing great today! 🐕"
        }
        
        # Social posts need to be sent as form data
        import json
        form_data = {
            'post_data': json.dumps(post_data)
        }
        
        url = f"{self.api_url}/social/posts"
        test_headers = {}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing Create Social Post...")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, data=form_data, headers=test_headers)
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    print("   Social post created successfully")
                    return True
                except:
                    return True
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_get_social_posts(self):
        """Test getting social posts"""
        return self.run_test("Get Social Posts", "GET", "social/posts", 200)

    def test_ai_vet_chat(self):
        """Test AI vet chat functionality"""
        chat_data = {
            "message": "My dog seems a bit lethargic today. Should I be concerned?"
        }
        
        success, response = self.run_test(
            "AI Vet Chat",
            "POST",
            "ai-vet/chat",
            200,
            data=chat_data
        )
        
        if success and 'response' in response:
            print("   AI Vet responded successfully")
            return True
        return False

    # Marketplace Tests
    def test_marketplace_categories(self):
        """Test getting marketplace categories"""
        success, response = self.run_test(
            "Get Marketplace Categories",
            "GET",
            "marketplace/categories",
            200
        )
        
        if success and isinstance(response, dict):
            print(f"   Found {len(response)} categories")
            return True
        return False

    def test_create_marketplace_listing(self):
        """Test creating a marketplace listing"""
        listing_data = {
            "title": "Golden Retriever Puppy",
            "description": "Beautiful and healthy Golden Retriever puppy looking for a loving home.",
            "category": "pets",
            "subcategory": "dogs",
            "price": 800.0,
            "currency": "USD",
            "condition": "new",
            "location": "New York, NY",
            "contact_phone": "+1-555-123-4567",
            "contact_email": "seller@example.com",
            "is_negotiable": True,
            "tags": ["puppy", "golden retriever", "friendly"],
            "pet_details": {
                "age": "8 weeks",
                "breed": "Golden Retriever",
                "gender": "male",
                "vaccinated": True
            }
        }
        
        success, response = self.run_test(
            "Create Marketplace Listing",
            "POST",
            "marketplace/listings",
            200,
            data=listing_data
        )
        
        if success and 'id' in response:
            self.listing_id = response['id']
            print(f"   Created listing: {response.get('title')} (ID: {self.listing_id})")
            return True
        return False

    def test_get_marketplace_listings(self):
        """Test getting marketplace listings"""
        success, response = self.run_test(
            "Get Marketplace Listings",
            "GET",
            "marketplace/listings",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} listings")
            return True
        return False

    def test_get_marketplace_listings_with_filters(self):
        """Test getting marketplace listings with filters"""
        success, response = self.run_test(
            "Get Marketplace Listings (Filtered)",
            "GET",
            "marketplace/listings?category=pets&min_price=500&max_price=1000",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} filtered listings")
            return True
        return False

    def test_get_specific_marketplace_listing(self):
        """Test getting specific marketplace listing"""
        if not hasattr(self, 'listing_id') or not self.listing_id:
            print("❌ No listing ID available for specific listing test")
            return False
            
        success, response = self.run_test(
            "Get Specific Marketplace Listing",
            "GET",
            f"marketplace/listings/{self.listing_id}",
            200
        )
        
        if success and 'id' in response:
            print(f"   Retrieved listing: {response.get('title')}")
            print(f"   Views: {response.get('views', 0)}")
            return True
        return False

    def test_update_marketplace_listing(self):
        """Test updating marketplace listing"""
        if not hasattr(self, 'listing_id') or not self.listing_id:
            print("❌ No listing ID available for update test")
            return False
            
        update_data = {
            "price": 750.0,
            "description": "Updated description - Beautiful and healthy Golden Retriever puppy with updated price.",
            "is_negotiable": False
        }
        
        success, response = self.run_test(
            "Update Marketplace Listing",
            "PUT",
            f"marketplace/listings/{self.listing_id}",
            200,
            data=update_data
        )
        
        if success and 'id' in response:
            print(f"   Updated listing price to: ${response.get('price')}")
            return True
        return False

    def test_upload_listing_images(self):
        """Test uploading images to marketplace listing"""
        if not hasattr(self, 'listing_id') or not self.listing_id:
            print("❌ No listing ID available for image upload test")
            return False
        
        # Create test images (1x1 pixel PNG)
        test_image_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGA4nEKtAAAAABJRU5ErkJggg=="
        )
        
        files = [
            ('files', ('test_image1.png', test_image_data, 'image/png')),
            ('files', ('test_image2.png', test_image_data, 'image/png'))
        ]
        
        success, response = self.run_test(
            "Upload Listing Images",
            "POST",
            f"marketplace/listings/{self.listing_id}/images",
            200,
            files=files
        )
        
        if success and 'message' in response:
            print(f"   {response.get('message')}")
            return True
        return False

    def test_get_my_marketplace_listings(self):
        """Test getting user's marketplace listings"""
        success, response = self.run_test(
            "Get My Marketplace Listings",
            "GET",
            "marketplace/my-listings",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} user listings")
            return True
        return False

    def test_toggle_favorite_listing(self):
        """Test toggling favorite status for a listing"""
        if not hasattr(self, 'listing_id') or not self.listing_id:
            print("❌ No listing ID available for favorite test")
            return False
            
        success, response = self.run_test(
            "Toggle Favorite Listing",
            "POST",
            f"marketplace/listings/{self.listing_id}/favorite",
            200
        )
        
        if success and 'is_favorite' in response:
            print(f"   Favorite status: {response.get('is_favorite')}")
            return True
        return False

    def test_get_my_favorite_listings(self):
        """Test getting user's favorite listings"""
        success, response = self.run_test(
            "Get My Favorite Listings",
            "GET",
            "marketplace/my-favorites",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} favorite listings")
            return True
        return False

    def test_marketplace_search(self):
        """Test marketplace search functionality"""
        success, response = self.run_test(
            "Search Marketplace Listings",
            "GET",
            "marketplace/search?query=puppy&category=pets",
            200
        )
        
        if success and 'results' in response:
            print(f"   Search found {len(response.get('results', []))} results")
            return True
        return False

    def test_delete_marketplace_listing(self):
        """Test deleting marketplace listing"""
        if not hasattr(self, 'listing_id') or not self.listing_id:
            print("❌ No listing ID available for delete test")
            return False
            
        success, response = self.run_test(
            "Delete Marketplace Listing",
            "DELETE",
            f"marketplace/listings/{self.listing_id}",
            200
        )
        
        if success and 'message' in response:
            print(f"   {response.get('message')}")
            return True
        return False

    # NEW ENHANCED FEATURES TESTS
    
    def test_veterinary_clinics(self):
        """Test getting veterinary clinics"""
        success, response = self.run_test(
            "Get Veterinary Clinics",
            "GET",
            "veterinary-clinics",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} veterinary clinics")
            if len(response) > 0:
                self.clinic_id = response[0].get('id')
                print(f"   Using clinic ID: {self.clinic_id}")
            return True
        return False

    def test_daily_information(self):
        """Test getting daily information"""
        success, response = self.run_test(
            "Get Daily Information",
            "GET",
            "daily-information",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} daily information items")
            return True
        return False

    def test_generate_daily_information(self):
        """Test generating new daily information"""
        success, response = self.run_test(
            "Generate Daily Information",
            "POST",
            "daily-information/generate?category=nutrition&species=dog",
            200
        )
        
        if success and 'title' in response:
            print(f"   Generated: {response.get('title')}")
            return True
        return False

    # Enhanced Appointment System Tests
    def test_create_appointment_slot(self):
        """Test creating appointment slots"""
        if not hasattr(self, 'clinic_id') or not self.clinic_id:
            print("❌ No clinic ID available for appointment slot test")
            return False
            
        tomorrow = datetime.now() + timedelta(days=1)
        
        slot_data = {
            "clinic_id": self.clinic_id,
            "date": tomorrow.isoformat(),
            "start_time": "09:00",
            "end_time": "09:30",
            "appointment_type": "consultation",
            "duration_minutes": 30,
            "max_appointments": 1
        }
        
        success, response = self.run_test(
            "Create Appointment Slot",
            "POST",
            "appointment-slots",
            200,
            data=slot_data
        )
        
        if success and 'id' in response:
            self.slot_id = response['id']
            print(f"   Created appointment slot: {self.slot_id}")
            return True
        return False

    def test_get_appointment_slots(self):
        """Test getting appointment slots"""
        success, response = self.run_test(
            "Get Appointment Slots",
            "GET",
            "appointment-slots",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} appointment slots")
            return True
        return False

    def test_create_enhanced_appointment(self):
        """Test creating enhanced appointments"""
        if not self.pet_id or not hasattr(self, 'clinic_id') or not self.clinic_id:
            print("❌ Missing pet ID or clinic ID for appointment test")
            return False
            
        tomorrow = datetime.now() + timedelta(days=1)
        
        appointment_data = {
            "pet_id": self.pet_id,
            "clinic_id": self.clinic_id,
            "slot_id": getattr(self, 'slot_id', None),
            "appointment_date": tomorrow.isoformat(),
            "appointment_time": "09:00",
            "appointment_type": "checkup",
            "priority": "normal",
            "symptoms": "Regular checkup",
            "notes": "Annual wellness exam"
        }
        
        success, response = self.run_test(
            "Create Enhanced Appointment",
            "POST",
            "appointments",
            200,
            data=appointment_data
        )
        
        if success and 'id' in response:
            self.appointment_id = response['id']
            print(f"   Created appointment: {self.appointment_id}")
            print(f"   Confirmation code: {response.get('confirmation_code')}")
            return True
        return False

    def test_get_appointments(self):
        """Test getting user appointments"""
        success, response = self.run_test(
            "Get User Appointments",
            "GET",
            "appointments",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} appointments")
            return True
        return False

    def test_update_appointment(self):
        """Test updating appointment"""
        if not hasattr(self, 'appointment_id') or not self.appointment_id:
            print("❌ No appointment ID available for update test")
            return False
            
        update_data = {
            "status": "confirmed",
            "notes": "Updated appointment notes"
        }
        
        success, response = self.run_test(
            "Update Appointment",
            "PUT",
            f"appointments/{self.appointment_id}",
            200,
            data=update_data
        )
        
        if success:
            print("   Appointment updated successfully")
            return True
        return False

    def test_cancel_appointment(self):
        """Test canceling appointment"""
        if not hasattr(self, 'appointment_id') or not self.appointment_id:
            print("❌ No appointment ID available for cancel test")
            return False
            
        success, response = self.run_test(
            "Cancel Appointment",
            "DELETE",
            f"appointments/{self.appointment_id}",
            200
        )
        
        if success:
            print("   Appointment canceled successfully")
            return True
        return False

    # Notification System Tests
    def test_get_notifications(self):
        """Test getting user notifications"""
        success, response = self.run_test(
            "Get User Notifications",
            "GET",
            "notifications",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} notifications")
            if len(response) > 0:
                self.notification_id = response[0].get('id')
            return True
        return False

    def test_mark_notification_read(self):
        """Test marking notification as read"""
        if not hasattr(self, 'notification_id') or not self.notification_id:
            print("❌ No notification ID available for mark read test")
            return False
            
        success, response = self.run_test(
            "Mark Notification Read",
            "PUT",
            f"notifications/{self.notification_id}/read",
            200
        )
        
        if success:
            print("   Notification marked as read")
            return True
        return False

    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        success, response = self.run_test(
            "Mark All Notifications Read",
            "POST",
            "notifications/mark-all-read",
            200
        )
        
        if success:
            print("   All notifications marked as read")
            return True
        return False

    # Review System Tests
    def test_create_review(self):
        """Test creating a review"""
        if not hasattr(self, 'clinic_id') or not self.clinic_id:
            print("❌ No clinic ID available for review test")
            return False
            
        review_data = {
            "target_type": "clinic",
            "target_id": self.clinic_id,
            "rating": 5,
            "title": "Excellent service",
            "comment": "The staff was very professional and caring. Highly recommend!",
            "is_anonymous": False
        }
        
        success, response = self.run_test(
            "Create Review",
            "POST",
            "reviews",
            200,
            data=review_data
        )
        
        if success and 'id' in response:
            self.review_id = response['id']
            print(f"   Created review: {response.get('title')}")
            return True
        return False

    def test_get_reviews(self):
        """Test getting reviews"""
        if not hasattr(self, 'clinic_id') or not self.clinic_id:
            print("❌ No clinic ID available for get reviews test")
            return False
            
        success, response = self.run_test(
            "Get Reviews",
            "GET",
            f"reviews?target_type=clinic&target_id={self.clinic_id}",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} reviews")
            return True
        return False

    # Analytics Tests
    def test_track_activity(self):
        """Test tracking user activity"""
        activity_data = {
            "activity_type": "page_view",
            "details": {
                "page": "dashboard",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        success, response = self.run_test(
            "Track User Activity",
            "POST",
            "analytics/track",
            200,
            data=activity_data
        )
        
        if success:
            print("   Activity tracked successfully")
            return True
        return False

    def test_get_analytics_dashboard(self):
        """Test getting analytics dashboard"""
        success, response = self.run_test(
            "Get Analytics Dashboard",
            "GET",
            "analytics/dashboard",
            200
        )
        
        if success and isinstance(response, dict):
            print(f"   Analytics dashboard loaded with {len(response)} metrics")
            return True
        return False

    # Enhanced Dashboard Tests
    def test_user_dashboard(self):
        """Test getting user dashboard"""
        success, response = self.run_test(
            "Get User Dashboard",
            "GET",
            "user/dashboard",
            200
        )
        
        if success and isinstance(response, dict):
            print(f"   Dashboard loaded with {len(response)} sections")
            return True
        return False

    def test_pet_health_summary(self):
        """Test getting pet health summary"""
        if not self.pet_id:
            print("❌ No pet ID available for health summary test")
            return False
            
        success, response = self.run_test(
            "Get Pet Health Summary",
            "GET",
            f"pets/{self.pet_id}/health-summary",
            200
        )
        
        if success and isinstance(response, dict):
            print("   Pet health summary loaded")
            return True
        return False

    # Vaccination Management Tests
    def test_add_vaccination_record(self):
        """Test adding vaccination record"""
        if not self.pet_id:
            print("❌ No pet ID available for vaccination test")
            return False
            
        vaccination_data = {
            "vaccine_name": "Rabies",
            "vaccination_date": datetime.now().isoformat(),
            "next_due_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "veterinarian": "Dr. Smith",
            "clinic_name": "City Pet Hospital",
            "batch_number": "RB2024001",
            "notes": "Annual rabies vaccination"
        }
        
        success, response = self.run_test(
            "Add Vaccination Record",
            "POST",
            f"pets/{self.pet_id}/vaccination-record",
            200,
            data=vaccination_data
        )
        
        if success and 'id' in response:
            print(f"   Added vaccination record: {response.get('vaccine_name')}")
            return True
        return False

    def test_get_vaccination_records(self):
        """Test getting vaccination records"""
        if not self.pet_id:
            print("❌ No pet ID available for vaccination records test")
            return False
            
        success, response = self.run_test(
            "Get Vaccination Records",
            "GET",
            f"pets/{self.pet_id}/vaccination-records",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} vaccination records")
            return True
        return False

    # Global Search Tests
    def test_global_search(self):
        """Test global search functionality"""
        success, response = self.run_test(
            "Global Search",
            "GET",
            "search/global?query=dog&type=all",
            200
        )
        
        if success and isinstance(response, dict):
            results = response.get('results', [])
            print(f"   Global search found {len(results)} results")
            return True
        return False

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting Pet Companion API Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 60)
        
        # Basic API tests
        self.test_health_check()
        self.test_root_endpoint()
        
        # Authentication tests
        if not self.test_user_registration():
            print("❌ User registration failed, stopping tests")
            return False
            
        # Pet management tests
        if not self.test_pet_creation():
            print("❌ Pet creation failed, stopping pet-related tests")
        else:
            self.test_get_user_pets()
            self.test_get_specific_pet()
            
            # AI feature tests (require pet)
            print("\n🤖 Testing AI Features...")
            self.test_health_analysis()
            self.test_get_health_analyses()
            self.test_daily_tip()
            self.test_ai_vet_chat()
            
            # Social feature tests
            print("\n👥 Testing Social Features...")
            self.test_social_post_creation()
            self.test_get_social_posts()
        
        # General feature tests
        self.test_recovery_stories()
        
        # Veterinary Directory Tests
        print("\n🏥 Testing Veterinary Directory...")
        self.test_veterinary_clinics()
        
        # Daily Information Tests
        print("\n📚 Testing Daily Information...")
        self.test_daily_information()
        self.test_generate_daily_information()
        
        # Enhanced Appointment System Tests
        print("\n📅 Testing Enhanced Appointment System...")
        if hasattr(self, 'clinic_id') and self.clinic_id:
            self.test_create_appointment_slot()
            self.test_get_appointment_slots()
            self.test_create_enhanced_appointment()
            self.test_get_appointments()
            if hasattr(self, 'appointment_id') and self.appointment_id:
                self.test_update_appointment()
                self.test_cancel_appointment()
        
        # Notification System Tests
        print("\n🔔 Testing Notification System...")
        self.test_get_notifications()
        if hasattr(self, 'notification_id') and self.notification_id:
            self.test_mark_notification_read()
        self.test_mark_all_notifications_read()
        
        # Review System Tests
        print("\n⭐ Testing Review System...")
        if hasattr(self, 'clinic_id') and self.clinic_id:
            self.test_create_review()
            self.test_get_reviews()
        
        # Analytics Tests
        print("\n📊 Testing Analytics...")
        self.test_track_activity()
        self.test_get_analytics_dashboard()
        
        # Enhanced Dashboard Tests
        print("\n🏠 Testing Enhanced Dashboard...")
        self.test_user_dashboard()
        if self.pet_id:
            self.test_pet_health_summary()
        
        # Vaccination Management Tests
        print("\n💉 Testing Vaccination Management...")
        if self.pet_id:
            self.test_add_vaccination_record()
            self.test_get_vaccination_records()
        
        # Global Search Tests
        print("\n🔍 Testing Global Search...")
        self.test_global_search()
        
        # Marketplace feature tests
        print("\n🛒 Testing Marketplace Features...")
        self.test_marketplace_categories()
        self.test_get_marketplace_listings()
        
        # Create a listing for further tests
        if self.test_create_marketplace_listing():
            self.test_get_marketplace_listings_with_filters()
            self.test_get_specific_marketplace_listing()
            self.test_update_marketplace_listing()
            self.test_upload_listing_images()
            self.test_get_my_marketplace_listings()
            self.test_toggle_favorite_listing()
            self.test_get_my_favorite_listings()
            self.test_marketplace_search()
            # Delete listing at the end
            self.test_delete_marketplace_listing()
        else:
            print("❌ Marketplace listing creation failed, skipping related tests")
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed")
            return False

def main():
    tester = PetCompanionAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())