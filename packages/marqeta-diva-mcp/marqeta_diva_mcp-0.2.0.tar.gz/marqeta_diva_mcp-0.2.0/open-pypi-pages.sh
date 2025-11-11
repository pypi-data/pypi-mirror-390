#!/bin/bash
# Quick script to open all PyPI registration pages

echo "Opening PyPI registration pages in your browser..."
echo ""
echo "Step 1: TestPyPI Registration"
open "https://test.pypi.org/account/register/"
sleep 2

echo "Step 2: PyPI Registration"
open "https://pypi.org/account/register/"
sleep 2

echo ""
echo "After registering and verifying your email, run:"
echo ""
echo "Step 3: TestPyPI Token"
echo "open 'https://test.pypi.org/manage/account/token/'"
echo ""
echo "Step 4: PyPI Token"
echo "open 'https://pypi.org/manage/account/token/'"
echo ""
echo "Instructions:"
echo "1. Register on both sites with: zvika.badalov@finally.com"
echo "2. Check your email and verify both accounts"
echo "3. Then open the token pages above"
echo "4. Create tokens named: marqeta-diva-mcp-upload"
echo "5. Scope: 'Entire account'"
echo "6. Copy and save both tokens securely!"
