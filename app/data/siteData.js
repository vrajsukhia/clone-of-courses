export const site = {
  name: "Great Learning",
  tagline: "",
  badge: "Free learning track with certificate",
};

export const profile = {
  name: "Ashray Soni",
  title: "Data Visualization Learner",
  email: "ashray.soni@example.com",
  phone: "+91 90000 00000",
  location: "Vadodara, India",
  memberSince: "2024",
  education: "B.Sc. Computer Science",
  institution: "University campus",
  focus: "Business Intelligence and Reporting",
  learningHours: "42 hours",
  bio:
    "Focused on turning raw data into executive-ready dashboards and storytelling.",
  skills: [
    "Power BI",
    "DAX basics",
    "SQL fundamentals",
    "Dashboard design",
    "Data storytelling",
  ],
  certificates: ["Data Visualization With Power BI"],
};

export const course = {
  id: "power-bi",
  slug: "data-visualization-with-power-bi",
  title: "Data Visualization With Power BI",
  summary:
    "Design crisp dashboards, build a semantic model, and communicate insights with confidence.",
  level: "Beginner",
  duration: "6 hours",
  lessons: 26,
  rating: "4.8",
  learners: "18k",
  certificate: "Verified certificate included",
  skills: [
    "Data modeling",
    "DAX basics",
    "Dashboard design",
    "Executive storytelling",
    "Power BI publishing",
  ],
  outcomes: [
    "Create a clean report layout with reusable theme tokens.",
    "Build measures that answer the most common business questions.",
    "Design a multi-page dashboard with navigation and tooltips.",
    "Publish and share securely with role-based access.",
  ],
  modules: [
    {
      title: "Foundations of Visual Storytelling",
      lessons: [
        { title: "What makes a visual memorable", length: "12 min" },
        { title: "Choosing the right chart", length: "18 min" },
        { title: "Designing for scannability", length: "15 min" },
        { title: "Story arcs for business data", length: "16 min" },
      ],
    },
    {
      title: "Power BI Desktop and Data Prep",
      lessons: [
        { title: "Touring the workspace", length: "10 min" },
        { title: "Cleaning data with Power Query", length: "22 min" },
        { title: "Shaping tables for analysis", length: "17 min" },
        { title: "Setting data types and formatting", length: "14 min" },
      ],
    },
    {
      title: "Modeling and Measures",
      lessons: [
        { title: "Star schema fundamentals", length: "19 min" },
        { title: "Relationship tuning", length: "14 min" },
        { title: "First DAX measures", length: "20 min" },
        { title: "Time intelligence shortcuts", length: "18 min" },
      ],
    },
    {
      title: "Dashboard Design",
      lessons: [
        { title: "Building a KPI bar", length: "13 min" },
        { title: "Drill-through and tooltips", length: "18 min" },
        { title: "Theme and color systems", length: "16 min" },
        { title: "Layout grids that scale", length: "14 min" },
      ],
    },
    {
      title: "Publish and Share",
      lessons: [
        { title: "Publishing to the service", length: "11 min" },
        { title: "Sharing and permissions", length: "16 min" },
        { title: "Refreshing datasets", length: "13 min" },
      ],
    },
    {
      title: "Capstone: Insight Storyboard",
      lessons: [
        { title: "Briefing and requirements", length: "12 min" },
        { title: "Build the dashboard", length: "28 min" },
        { title: "Review and finalize", length: "14 min" },
      ],
    },
  ],
};

export const courses = [
  {
    id: "power-bi",
    title: "Data Visualization With Power BI",
    slug: "data-visualization-with-power-bi",
    level: "Beginner",
    duration: "6 hours",
    lessons: 26,
    tag: "Certificate",
    summary: "Craft dashboards that executives can read in 60 seconds.",
    image: "/academy-assets/assets/images/gla-home-page/free-course-desk-new-us-banner.jpg",
    partner: "Microsoft",
    partnerLogo: "/academy-assets/assets/microsoft.png",
    projects: 2,
    videoContent: "6 hrs video content",
    tier: "PRO",
  },
  {
    id: "excel-analytics",
    title: "Excel Essentials for Analysts",
    level: "Beginner",
    duration: "4 hours",
    lessons: 18,
    tag: "New",
    summary: "Build clean models with formulas, pivots, and charts.",
    image: "/academy-assets/assets/images/gla-home-page/free-course-desk-new-us-banner.jpg",
    partner: "Microsoft",
    partnerLogo: "/academy-assets/assets/microsoft.png",
    projects: 2,
    videoContent: "4 hrs video content",
    tier: "PRO",
  },
  {
    id: "data-storytelling",
    title: "Data Storytelling for Leaders",
    level: "Intermediate",
    duration: "3 hours",
    lessons: 14,
    tag: "Popular",
    summary: "Turn metrics into narratives that drive decisions.",
    image: "/academy-assets/assets/images/gla-home-page/free-course-desk-new-us-banner.jpg",
    partner: "AWS",
    partnerLogo: "/academy-assets/assets/aws.png",
    projects: 1,
    videoContent: "3 hrs video content",
    tier: "FREE",
  },
  {
    id: "dashboard-design",
    title: "Dashboard Design Systems",
    level: "Intermediate",
    duration: "5 hours",
    lessons: 21,
    tag: "Design",
    summary: "Create a consistent visual language across teams.",
    image: "/academy-assets/assets/images/gla-home-page/free-course-desk-new-us-banner.jpg",
    partner: "Microsoft",
    partnerLogo: "/academy-assets/assets/microsoft.png",
    projects: 3,
    videoContent: "5 hrs video content",
    tier: "PRO",
  },
];

export const stats = [
  { value: "150k+", label: "Learners active" },
  { value: "92%", label: "Course completion" },
  { value: "4.8/5", label: "Average rating" },
  { value: "300+", label: "Learning hours" },
];

export const features = [
  {
    title: "Hands-on project flow",
    description: "Practice in short sprints that build a full dashboard by the end.",
  },
  {
    title: "Built-in review checkpoints",
    description: "Each module ends with a quick diagnostic to lock in progress.",
  },
  {
    title: "Certificate ready",
    description: "Finish the course and download a verified certificate instantly.",
  },
  {
    title: "Profile-ready showcase",
    description: "Add the course badge and completion story to your profile.",
  },
];

export const testimonials = [
  {
    name: "Ritika J.",
    role: "Business Analyst",
    quote:
      "The layout guidance and Power BI tricks made my dashboards feel executive-ready.",
  },
  {
    name: "Ahmed S.",
    role: "Operations Lead",
    quote:
      "I finished the capstone and used it to pitch a new report structure to my team.",
  },
  {
    name: "Priya D.",
    role: "BI Intern",
    quote:
      "Clear, direct lessons with just enough practice to stay confident.",
  },
];

export const faqs = [
  {
    question: "Is this course really free?",
    answer: "Yes. This track is free to enroll and complete with a certificate.",
  },
  {
    question: "Do I need Power BI experience?",
    answer: "No. We start from the basics and build to multi-page dashboards.",
  },
  {
    question: "Can I download the certificate?",
    answer: "Once you mark the course complete, the certificate download unlocks.",
  },
];

export const learningSteps = [
  {
    title: "Enroll and set your pace",
    description: "Pick a daily target and the course adapts your timeline.",
  },
  {
    title: "Build with guided labs",
    description: "Each module comes with a mini brief and practice file.",
  },
  {
    title: "Ship the capstone",
    description: "Finish the storyboard and publish your dashboard.",
  },
];
