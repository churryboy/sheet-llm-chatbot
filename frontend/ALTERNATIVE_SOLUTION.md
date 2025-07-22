# Alternative Solution: Using Google Forms

Since Google is blocking the Apps Script due to security concerns, here's an alternative approach using Google Forms:

## Option 1: Create a Google Form

1. Go to [Google Forms](https://forms.google.com)
2. Create a new form with these fields:
   - 이름 (Short answer)
   - 출생년도 (Short answer)
   - 학년 (Dropdown)
   - 학교 이름 (Short answer)
   - 거주 도시 (Short answer)
   - 내신 점수 (Short answer)
   - 모의고사 점수 (Short answer)
   - 공부 스타일 (Paragraph)
   - 선호하는 공부법 (Paragraph)
   - 공부하면서 힘든 부분 (Paragraph)
   - 콴다에 바라는 기능 (Paragraph)

3. Link the form to your Google Sheet
4. Get the form's public URL
5. Update the button to redirect to the Google Form

## Option 2: Use a Different Backend Service

Instead of Google Apps Script, you could use:

1. **Netlify Functions** (since you're already using Vercel)
2. **Firebase Functions**
3. **A simple Node.js server**

## Option 3: Manual Apps Script Setup (For Testing)

If you want to continue with Apps Script:

1. In the Apps Script editor, add both scripts:
   - The main script from `google-apps-script-safe.js`
   - The test function from `test-manual.js`

2. Run the `testAddData()` function manually:
   - Select `testAddData` from the function dropdown
   - Click the Run button
   - Grant permissions when asked

3. Check if data appears in your Google Sheet

4. If it works, the issue is with deployment permissions, not the code

## Option 4: Use Google Workspace Account

The security block often happens with personal Google accounts. If you have access to a Google Workspace (formerly G Suite) account:

1. Use the Workspace account to create the Apps Script
2. Deploy from that account
3. Security warnings are less strict for Workspace accounts

## Temporary Solution

For now, you can:

1. Keep the "Add Data" button
2. Have it redirect to a Google Form
3. Later migrate to a proper backend solution

Would you like me to help you set up any of these alternatives?
