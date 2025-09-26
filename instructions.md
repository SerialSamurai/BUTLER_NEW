# Claude Code Instructions for BUTLER Demo Setup

## Quick Demo Setup (Choose One)

### Option 1: Open Standalone HTML (Fastest)
```bash
# Just open the HTML file in default browser
open butler-standalone.html
# OR
xdg-open butler-standalone.html
```

### Option 2: Run Next.js Development Server
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
```

## File Structure Expected
```
/
├── butler-standalone.html  (Complete demo in single file)
├── package.json            (Node dependencies)
├── components/
│   └── ButlerSystem.tsx   (Main React component)
├── pages/
│   ├── index.tsx          (Home page)
│   └── _app.tsx           (App wrapper)
├── styles/
│   └── globals.css        (Tailwind styles)
├── tailwind.config.js     (Tailwind config)
├── tsconfig.json          (TypeScript config)
├── next.config.js         (Next.js config)
└── postcss.config.js      (PostCSS config)
```

## Demo Talking Points

1. **Show the dashboard** - Point out the real-time metrics at the top
2. **Click "Listserv Monitor" tab** - Show email integration
3. **Click on any email** - Demonstrates AI analysis
4. **Type test queries** in chat:
   - "What's the weather alert?"
   - "Check system status"
   - "How many emails today?"
5. **Highlight simplicity** - Clean government-appropriate design

## If Files Are Missing

```bash
# Create any missing directories
mkdir -p components pages styles

# If npm packages aren't installed
npm install next react react-dom lucide-react
npm install -D typescript @types/react @types/node tailwindcss
```

## Browser Compatibility
- Works in Chrome, Firefox, Safari, Edge
- Standalone HTML has all dependencies included via CDN
- No backend server required for demo

## For Production Discussion
- Mention on-premise deployment option
- Discuss integration with existing Dallas County email servers
- Note that this is a UI prototype - backend AI integration would be next step