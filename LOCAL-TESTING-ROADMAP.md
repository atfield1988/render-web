# 🧪 Local Testing Roadmap - Step by Step

## 📋 Complete Guide for Local Environment Testing

This guide will help you test everything locally before AWS deployment.

---

## ✅ Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.11 installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] PostgreSQL installed locally
- [ ] Git installed (optional)
- [ ] Code editor (VS Code recommended)

---

## 📁 Phase 1: Project Setup (10 minutes)

### Step 1.1: Verify Project Structure

```bash
cd renew-parktel-schedule-system
```

Check that you have:
```
renew-parktel-schedule-system/
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── requirements.txt
│   └── renew-.env.example
└── frontend/
    ├── src/
    ├── public/
    └── package.json (needs to be copied)
```

### Step 1.2: Copy Missing Frontend Files

```bash
# Copy all frontend files from old project
cd frontend

# Copy package.json
cp ../../parktel-schedule-system/frontend/package.json .

# Copy all source files
cp -r ../../parktel-schedule-system/frontend/src/* src/
cp -r ../../parktel-schedule-system/frontend/public/* public/

# Verify files copied
ls src/
ls public/
```

**Expected files in src/:**
- index.js
- App.js
- index.css
- components/ (Header.js, Footer.js, Layout.js, ProtectedRoute.js)
- contexts/ (AuthContext.js)
- services/ (api.js)
- pages/ (Home.js, Login.js, etc.)

---

## 📁 Phase 2: Backend Setup (15 minutes)

### Step 2.1: Setup PostgreSQL Database

```bash
# Start PostgreSQL service
# Windows: Start from Services
# Mac: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Create database
psql -U postgres
```

In PostgreSQL:
```sql
CREATE DATABASE parkteldb_local;
CREATE USER parktel_user WITH PASSWORD 'parktel_local_pass';
GRANT ALL PRIVILEGES ON DATABASE parkteldb_local TO parktel_user;
\q
```

### Step 2.2: Configure Environment

```bash
cd backend

# Copy environment file
cp renew-.env.example .env

# Edit .env file
nano .env
```

Set these values in `.env`:
```bash
DATABASE_URL=postgresql+psycopg2://parktel_user:parktel_local_pass@localhost:5432/parkteldb_local
SECRET_KEY=local_dev_secret_key_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Optional (for local testing, can be empty)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=ap-northeast-2
CLOUDWATCH_LOG_GROUP=
CLOUDWATCH_LOG_STREAM=
```

### Step 2.3: Install Python Dependencies

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected output:** All packages installed successfully

### Step 2.4: Initialize Database

```bash
# Run Alembic migrations
alembic upgrade head

# Create initial admin users
python -m app.init_db
```

**Expected output:**
```
Creating super_admin user (supernova)...
super_admin 'supernova' created.
Creating admin user (olympic88)...
admin 'olympic88' created.
```

### Step 2.5: Start Backend Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Test backend:**
Open browser: `http://localhost:8000`

Should see:
```json
{"message": "서울올림픽파크텔 API"}
```

---

## 📁 Phase 3: Frontend Setup (10 minutes)

### Step 3.1: Configure API URL

```bash
# Open new terminal
cd frontend/src/services

# Edit api.js
nano api.js
```

Change API URL to local:
```javascript
// Change this line:
const API_BASE_URL = 'http://YOUR_EC2_IP_OR_CLOUDFRONT_URL:8000/api';

// To this (for local testing):
const API_BASE_URL = 'http://localhost:8000/api';
```

### Step 3.2: Install Frontend Dependencies

```bash
cd frontend

# Install dependencies
npm install
```

**Expected output:** All packages installed successfully

### Step 3.3: Start Frontend Server

```bash
# Start React development server
npm start
```

**Expected output:**
```
Compiled successfully!
Local:            http://localhost:3000
```

Browser should automatically open to `http://localhost:3000`

---

## 📁 Phase 4: Functional Testing (30 minutes)

### Test 4.1: Homepage (Public Access)

**URL:** `http://localhost:3000`

**Test:**
- [ ] Homepage loads without errors
- [ ] Banner carousel displays (3 images)
- [ ] Schedule list displays (empty initially)
- [ ] Navigation menu visible
- [ ] Footer displays

**Expected:** All elements load, no console errors

---

### Test 4.2: User Registration

**Steps:**
1. Click "회원가입" (Register)
2. Enter phone number: `01012345678`
3. Click submit

**Expected:**
- [ ] Success message: "회원가입 신청이 완료되었습니다"
- [ ] Message shows: "임시 비밀번호: abcd1234"
- [ ] Redirects to login page

---

### Test 4.3: Admin Login

**Steps:**
1. Go to Admin Login page
2. Username: `supernova`
3. Password: `kspo88!`
4. Click login

**Expected:**
- [ ] Login successful
- [ ] Redirects to Admin Dashboard
- [ ] Shows "supernova님, 환영합니다"

---

### Test 4.4: User Approval (Admin)

**Steps:**
1. In Admin Dashboard
2. Check "신규 회원 승인 대기 목록"
3. Find user `01012345678`
4. Click "승인" (Approve)

**Expected:**
- [ ] User approved
- [ ] User removed from pending list
- [ ] Success message displayed

---

### Test 4.5: User Login

**Steps:**
1. Logout from admin
2. Go to User Login
3. Phone: `01012345678`
4. Password: `abcd1234`
5. Click login

**Expected:**
- [ ] Login successful
- [ ] Redirects to Mypage
- [ ] Shows user phone number

---

### Test 4.6: Schedule Creation (Admin)

**Steps:**
1. Login as admin (supernova)
2. Go to Admin Dashboard
3. Create new schedule:
   - Title: "테스트 근무"
   - Date: Tomorrow
   - Start time: "09:00"
   - End time: "18:00"
   - Capacity: 3
4. Click create

**Expected:**
- [ ] Schedule created successfully
- [ ] Appears in schedule list
- [ ] Shows on homepage

---

### Test 4.7: Schedule Application (User)

**Steps:**
1. Login as user (`01012345678`)
2. Go to Homepage
3. Find "테스트 근무" schedule
4. Click "상세보기"
5. Click "이 스케줄에 신청하기"

**Expected:**
- [ ] Application submitted
- [ ] Success message displayed
- [ ] Redirects to Mypage
- [ ] Application appears in "나의 신청 내역"

---

### Test 4.8: Application Approval (Admin)

**Steps:**
1. Login as admin
2. Go to schedule detail page
3. See applicant list
4. Click "승인" for the application

**Expected:**
- [ ] Application approved
- [ ] Status changes to "approved"
- [ ] current_applicants increases

---

### Test 4.9: Application Cancellation (User)

**Steps:**
1. Create another application (as user)
2. Go to Mypage
3. Find pending application
4. Click "취소" button

**Expected:**
- [ ] Application cancelled (only if pending)
- [ ] Removed from list
- [ ] Success message

---

### Test 4.10: Notice Creation (Admin)

**Steps:**
1. Login as admin
2. Go to Admin Dashboard → Notices tab
3. Create notice:
   - Title: "테스트 공지"
   - Content: "테스트 내용입니다"
   - Pinned: Yes
4. Click create

**Expected:**
- [ ] Notice created
- [ ] Appears in notice list
- [ ] Pinned notice shows first

---

### Test 4.11: Grant Admin Privilege (Super Admin Only)

**Steps:**
1. Login as supernova (super admin)
2. Go to Admin Dashboard
3. Find approved user
4. Click "관리자 권한 부여"
5. Enter username: `testadmin`
6. Confirm

**Expected:**
- [ ] User promoted to admin
- [ ] Can now access admin features
- [ ] Cannot grant admin to others (not super admin)

---

### Test 4.12: Public Schedule View (No Login)

**Steps:**
1. Logout completely
2. Go to Homepage
3. View schedule list

**Expected:**
- [ ] Schedules visible without login
- [ ] Can click "상세보기"
- [ ] Cannot apply (redirects to login)

---

## 📁 Phase 5: Error Testing (15 minutes)

### Test 5.1: Duplicate Registration

**Steps:**
1. Try to register with same phone number twice

**Expected:**
- [ ] Error: "이미 등록된 전화번호입니다"

---

### Test 5.2: Wrong Password

**Steps:**
1. Try to login with wrong password

**Expected:**
- [ ] Error: "비밀번호가 일치하지 않습니다"

---

### Test 5.3: Unapproved User Login

**Steps:**
1. Register new user
2. Try to login before admin approval

**Expected:**
- [ ] Error: "관리자 승인이 필요합니다"

---

### Test 5.4: Capacity Exceeded

**Steps:**
1. Create schedule with capacity 1
2. Have 2 users apply

**Expected:**
- [ ] Second user gets error: "근무 인원이 초과되었습니다"

---

### Test 5.5: Cancel Approved Application

**Steps:**
1. Try to cancel an approved application

**Expected:**
- [ ] Error: "승인된 신청은 취소할 수 없습니다"

---

## 📁 Phase 6: Database Verification (5 minutes)

### Step 6.1: Check Database Tables

```bash
psql -U parktel_user -d parkteldb_local
```

```sql
-- List all tables
\dt

-- Check users
SELECT id, phone_number, username, role, status FROM users;

-- Check schedules
SELECT id, title, work_date, capacity, current_applicants FROM schedules;

-- Check applications
SELECT id, user_id, schedule_id, status, created_at FROM applications;

-- Check notices
SELECT id, title, is_pinned, view_count FROM notices;

\q
```

**Expected:**
- [ ] All tables exist
- [ ] Data matches what you created
- [ ] Relationships work correctly

---

## 📁 Phase 7: Performance Testing (5 minutes)

### Test 7.1: API Response Time

```bash
# Test API endpoint
curl -w "@-" -o /dev/null -s http://localhost:8000/api/ <<'EOF'
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
      time_redirect:  %{time_redirect}\n
   time_pretransfer:  %{time_pretransfer}\n
 time_starttransfer:  %{time_starttransfer}\n
                    ----------\n
         time_total:  %{time_total}\n
EOF
```

**Expected:** time_total < 0.5 seconds

### Test 7.2: Frontend Load Time

**Steps:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Reload homepage
4. Check "Load" time

**Expected:** < 3 seconds

---

## ✅ Final Verification Checklist

### Backend
- [ ] Server starts without errors
- [ ] Database migrations successful
- [ ] Admin users created
- [ ] All API endpoints respond
- [ ] Authentication works
- [ ] Authorization works (roles)

### Frontend
- [ ] Homepage loads
- [ ] All pages accessible
- [ ] Images display
- [ ] Forms work
- [ ] Navigation works
- [ ] No console errors

### Features
- [ ] User registration works
- [ ] Admin approval works
- [ ] User login works
- [ ] Schedule CRUD works (admin)
- [ ] Notice CRUD works (admin)
- [ ] Application submission works
- [ ] Application approval works
- [ ] Application cancellation works (pending only)
- [ ] Grant admin works (super admin only)
- [ ] Public schedule view works

### Security
- [ ] Unapproved users cannot login
- [ ] Users cannot access admin pages
- [ ] Admins cannot grant admin privileges
- [ ] Only super admin can grant admin
- [ ] JWT tokens expire correctly
- [ ] Passwords are hashed

### Data Integrity
- [ ] CASCADE deletes work
- [ ] Capacity limits enforced
- [ ] Duplicate prevention works
- [ ] Status transitions correct

---

## 🎯 Success Criteria

Your local environment is ready for AWS deployment when:

✅ All 12 functional tests pass
✅ All 5 error tests pass
✅ Database verification complete
✅ Performance acceptable
✅ Final checklist 100% complete

---

## 📝 Common Issues & Solutions

### Issue 1: Database Connection Error
**Solution:** Check PostgreSQL is running, verify DATABASE_URL in .env

### Issue 2: Module Not Found
**Solution:** Activate virtual environment, reinstall requirements

### Issue 3: Port Already in Use
**Solution:** Kill process on port 8000 or 3000, or use different port

### Issue 4: CORS Errors
**Solution:** Check backend CORS settings in main.py

### Issue 5: Images Not Loading
**Solution:** Verify images copied to frontend/public/images/

---

## 🚀 Next Steps

After all tests pass:

1. **Document any issues** found during testing
2. **Fix any bugs** discovered
3. **Proceed to AWS deployment** using deployment guides
4. **Test again on AWS** after deployment

---

**Testing Time Estimate:**
- Setup: 35 minutes
- Testing: 50 minutes
- Verification: 10 minutes
- **Total: ~90 minutes**

**Status: Ready for Local Testing** ✅
