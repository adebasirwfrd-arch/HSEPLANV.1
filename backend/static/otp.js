// HSE OTP (Objectives, Targets and Program) JavaScript
(function () {
    var selectedOTPYear = 2025;
    var selectedOTPMonth = 'all';

    // OTP Data - 8 objectives, 55 programs
    var otpData = {
        2025: {
            objectives: [
                {
                    id: 1,
                    name: "Minimize Motor Vehicle Crash (MVC)",
                    target: "Zero Preventable Vehicle Incident (PVI)",
                    programs: [
                        { id: 1, name: "Provide weekly Driver driving performance report (RAG) for review", plan: "4 report/Month", responsible: "HSE", progress: 92, monthly: { jan: { p: 4, a: 4 }, feb: { p: 4, a: 4 }, mar: { p: 4, a: 4 }, apr: { p: 4, a: 4 }, may: { p: 4, a: 4 }, jun: { p: 4, a: 4 }, jul: { p: 4, a: 4 }, aug: { p: 4, a: 4 }, sep: { p: 4, a: 4 }, oct: { p: 4, a: 4 }, nov: { p: 4, a: 4 }, dec: { p: 4, a: 0 } } },
                        { id: 2, name: "Conduct Driver and Vehicle Safety Standard Audit", plan: "3 Base in a Year", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 1, a: 1 }, aug: { p: 1, a: 1 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 3, name: "Conduct vehicle compliance spot check", plan: "Monthly", responsible: "Supervisor", progress: 96, monthly: { jan: { p: 2, a: 3 }, feb: { p: 2, a: 2 }, mar: { p: 2, a: 2 }, apr: { p: 2, a: 2 }, may: { p: 2, a: 2 }, jun: { p: 2, a: 2 }, jul: { p: 2, a: 2 }, aug: { p: 2, a: 2 }, sep: { p: 2, a: 2 }, oct: { p: 2, a: 2 }, nov: { p: 2, a: 2 }, dec: { p: 2, a: 0 } } },
                        { id: 4, name: "Driving Safety Campaign for All Indonesia Base", plan: "One times in year", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 1, a: 1 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 5, name: "Review Driver Driving performance", plan: "Monthly", responsible: "HSE", progress: 100, monthly: { jan: { p: 1, a: 1 }, feb: { p: 1, a: 1 }, mar: { p: 1, a: 1 }, apr: { p: 1, a: 2 }, may: { p: 1, a: 1 }, jun: { p: 1, a: 1 }, jul: { p: 1, a: 1 }, aug: { p: 1, a: 1 }, sep: { p: 1, a: 1 }, oct: { p: 1, a: 1 }, nov: { p: 1, a: 1 }, dec: { p: 1, a: 0 } } },
                        { id: 6, name: "Conduct Driver Coaching for Yellow and Red Driver", plan: "Quarterly", responsible: "HSE", progress: 100, monthly: { jan: { p: 1, a: 1 }, feb: { p: 0, a: 1 }, mar: { p: 0, a: 1 }, apr: { p: 1, a: 1 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 1, a: 2 }, aug: { p: 0, a: 1 }, sep: { p: 0, a: 1 }, oct: { p: 1, a: 1 }, nov: { p: 0, a: 1 }, dec: { p: 0, a: 0 } } },
                        { id: 7, name: "Motor Vehicle Safety Training / Commentary Drive", plan: "Quarterly", responsible: "HSE", progress: 100, monthly: { jan: { p: 1, a: 1 }, feb: { p: 0, a: 1 }, mar: { p: 0, a: 1 }, apr: { p: 1, a: 1 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 1, a: 1 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 1 }, oct: { p: 1, a: 1 }, nov: { p: 0, a: 1 }, dec: { p: 0, a: 0 } } }
                    ]
                },
                {
                    id: 2,
                    name: "Improve Best Safety Culture and Compliance",
                    target: "Zero SIF and Good Safety Culture",
                    programs: [
                        { id: 8, name: "Submit RADAR Card intervention", plan: "24 cards/employee/year", responsible: "Manager/Supv", progress: 96, monthly: { jan: { p: 2, a: 2 }, feb: { p: 2, a: 3 }, mar: { p: 2, a: 2 }, apr: { p: 2, a: 2 }, may: { p: 2, a: 2 }, jun: { p: 2, a: 2 }, jul: { p: 2, a: 2 }, aug: { p: 2, a: 2 }, sep: { p: 2, a: 2 }, oct: { p: 2, a: 2 }, nov: { p: 2, a: 2 }, dec: { p: 2, a: 0 } } },
                        { id: 9, name: "Conduct HSE Monthly Meeting per Base", plan: "Monthly / Base", responsible: "Manager/Supv", progress: 92, monthly: { jan: { p: 3, a: 3 }, feb: { p: 3, a: 3 }, mar: { p: 3, a: 3 }, apr: { p: 3, a: 3 }, may: { p: 3, a: 3 }, jun: { p: 3, a: 3 }, jul: { p: 3, a: 3 }, aug: { p: 3, a: 3 }, sep: { p: 3, a: 3 }, oct: { p: 3, a: 3 }, nov: { p: 3, a: 3 }, dec: { p: 3, a: 0 } } },
                        { id: 10, name: "Conduct Facility Inspection", plan: "Monthly", responsible: "Manager/Supv", progress: 100, monthly: { jan: { p: 1, a: 2 }, feb: { p: 1, a: 3 }, mar: { p: 1, a: 3 }, apr: { p: 1, a: 2 }, may: { p: 1, a: 2 }, jun: { p: 1, a: 2 }, jul: { p: 1, a: 2 }, aug: { p: 1, a: 2 }, sep: { p: 1, a: 1 }, oct: { p: 1, a: 1 }, nov: { p: 1, a: 1 }, dec: { p: 1, a: 0 } } },
                        { id: 11, name: "Conduct Field Inspection / MWT", plan: "Quarterly", responsible: "Manager/Supv", progress: 100, monthly: { jan: { p: 1, a: 3 }, feb: { p: 0, a: 3 }, mar: { p: 0, a: 4 }, apr: { p: 1, a: 1 }, may: { p: 0, a: 1 }, jun: { p: 0, a: 1 }, jul: { p: 1, a: 2 }, aug: { p: 0, a: 2 }, sep: { p: 0, a: 1 }, oct: { p: 1, a: 2 }, nov: { p: 0, a: 2 }, dec: { p: 0, a: 0 } } },
                        { id: 12, name: "Leadership Safety Engagement (LSE)", plan: "Quarterly", responsible: "Country Ops Mgr", progress: 100, monthly: { jan: { p: 1, a: 1 }, feb: { p: 0, a: 1 }, mar: { p: 0, a: 1 }, apr: { p: 0, a: 1 }, may: { p: 1, a: 1 }, jun: { p: 0, a: 1 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 1 }, sep: { p: 1, a: 1 }, oct: { p: 0, a: 1 }, nov: { p: 0, a: 2 }, dec: { p: 0, a: 0 } } },
                        { id: 13, name: "HSE Reward program", plan: "3 reward/month/base", responsible: "Manager/Supv", progress: 92, monthly: { jan: { p: 1, a: 1 }, feb: { p: 1, a: 1 }, mar: { p: 1, a: 1 }, apr: { p: 1, a: 1 }, may: { p: 1, a: 1 }, jun: { p: 1, a: 1 }, jul: { p: 1, a: 1 }, aug: { p: 1, a: 1 }, sep: { p: 1, a: 1 }, oct: { p: 1, a: 1 }, nov: { p: 1, a: 1 }, dec: { p: 1, a: 0 } } },
                        { id: 14, name: "Conduct HSE induction/orientation training", plan: "100% new visitors", responsible: "HSE", progress: 92, monthly: { jan: { p: 1, a: 1 }, feb: { p: 1, a: 1 }, mar: { p: 1, a: 1 }, apr: { p: 1, a: 1 }, may: { p: 1, a: 1 }, jun: { p: 1, a: 1 }, jul: { p: 1, a: 1 }, aug: { p: 1, a: 1 }, sep: { p: 1, a: 1 }, oct: { p: 1, a: 1 }, nov: { p: 1, a: 1 }, dec: { p: 1, a: 0 } } },
                        { id: 15, name: "Conduct Contractor Audit", plan: "Annually", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 1, a: 1 }, sep: { p: 0, a: 1 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 16, name: "Conduct Contractor SQM Meeting", plan: "Annually", responsible: "Manager/Supv", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 1, a: 1 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 1 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 17, name: "Conduct Management Review Meeting", plan: "Annually", responsible: "Manager/Supv", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 1, a: 1 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 18, name: "Conduct P2K3 / safety committee meeting", plan: "3 times/Month/Base", responsible: "All Supervisor", progress: 92, monthly: { jan: { p: 3, a: 3 }, feb: { p: 3, a: 3 }, mar: { p: 3, a: 3 }, apr: { p: 3, a: 3 }, may: { p: 3, a: 3 }, jun: { p: 3, a: 3 }, jul: { p: 3, a: 3 }, aug: { p: 3, a: 3 }, sep: { p: 3, a: 3 }, oct: { p: 3, a: 3 }, nov: { p: 3, a: 3 }, dec: { p: 3, a: 0 } } },
                        { id: 19, name: "Provide P2K3 report to Disnaker", plan: "3 report/Quarter", responsible: "HSE", progress: 100, monthly: { jan: { p: 3, a: 3 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 3, a: 3 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 3, a: 3 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 3, a: 3 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } }
                    ]
                },
                {
                    id: 3,
                    name: "Minimize Risk from Facility Base",
                    target: "Zero SIF and Increase Compliance",
                    programs: [
                        { id: 20, name: "Conduct Facility device inspection", plan: "Monthly / Base", responsible: "Facility Supv", progress: 92, monthly: { jan: { p: 3, a: 3 }, feb: { p: 3, a: 3 }, mar: { p: 3, a: 3 }, apr: { p: 3, a: 3 }, may: { p: 3, a: 3 }, jun: { p: 3, a: 3 }, jul: { p: 3, a: 3 }, aug: { p: 3, a: 3 }, sep: { p: 3, a: 3 }, oct: { p: 3, a: 3 }, nov: { p: 3, a: 3 }, dec: { p: 3, a: 0 } } },
                        { id: 21, name: "Conduct facility hazard hunt", plan: "Monthly / Base", responsible: "Manager/Supv", progress: 94, monthly: { jan: { p: 3, a: 3 }, feb: { p: 3, a: 3 }, mar: { p: 3, a: 4 }, apr: { p: 3, a: 3 }, may: { p: 3, a: 3 }, jun: { p: 3, a: 3 }, jul: { p: 3, a: 3 }, aug: { p: 3, a: 3 }, sep: { p: 3, a: 3 }, oct: { p: 3, a: 3 }, nov: { p: 3, a: 3 }, dec: { p: 3, a: 0 } } },
                        { id: 22, name: "Annual maintenance of Firex", plan: "Annually / Base", responsible: "Facility Supv", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 1, a: 1 }, jul: { p: 0, a: 0 }, aug: { p: 1, a: 1 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 1, a: 1 }, dec: { p: 0, a: 0 } } },
                        { id: 23, name: "Annual Tool Rack Inspection", plan: "Annually / Base", responsible: "Facility Supv", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 1, a: 1 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 1, a: 1 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 1, a: 1 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 24, name: "Conduct DROPS Survey", plan: "Per Semester / Base", responsible: "Facility/HSE", progress: 100, monthly: { jan: { p: 3, a: 3 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 1, a: 1 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 1 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 25, name: "Conduct Facility Safety Standard Audit", plan: "Annually / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 1, a: 1 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } }
                    ]
                },
                {
                    id: 4,
                    name: "Improve HSE Competency of Personnel",
                    target: "Zero SIF and Improve Safety Awareness",
                    programs: [
                        { id: 26, name: "Conduct Safety 101, HSE Orientation", plan: "Per Semester / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 1, a: 1 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 1 }, apr: { p: 1, a: 1 }, may: { p: 1, a: 1 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 1 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 1 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 27, name: "Conduct DAMKAR D Training", plan: "Annually / Base", responsible: "HSE and OM", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 28, name: "Manual Handling Training", plan: "Annually / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 1, a: 1 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 1 }, sep: { p: 0, a: 1 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 29, name: "Refresh First Aid Training", plan: "Annually / Base", responsible: "HSE and OM", progress: 67, monthly: { jan: { p: 0, a: 0 }, feb: { p: 1, a: 1 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 1, a: 1 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 1, a: 0 } } },
                        { id: 30, name: "Internal Basic Fire Training", plan: "Annually / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 1, a: 1 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 1 }, apr: { p: 1, a: 1 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 1 }, sep: { p: 0, a: 0 }, oct: { p: 1, a: 1 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 31, name: "DROPS Object Awareness Training", plan: "Annually / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 1, a: 1 }, jul: { p: 0, a: 0 }, aug: { p: 1, a: 1 }, sep: { p: 1, a: 1 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 32, name: "Lifting & Rigging Operator Coaching", plan: "Quarterly / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 1, a: 1 }, mar: { p: 0, a: 1 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 1, a: 1 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 1, a: 1 }, dec: { p: 0, a: 0 } } },
                        { id: 33, name: "Hand and Finger Injury Prevention Training", plan: "Annually / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 1, a: 1 }, feb: { p: 1, a: 1 }, mar: { p: 1, a: 1 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } }
                    ]
                },
                {
                    id: 5,
                    name: "Identify the Risk and Create Control",
                    target: "Zero Serious Injury and Fatality (SIF)",
                    programs: [
                        { id: 34, name: "Review Legal Business Requirement", plan: "Annually / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 1, a: 1 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 35, name: "Review Generic Risk Assessment (TRA)", plan: "Annually / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 1, a: 1 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 1 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 36, name: "Review Emergency Response Procedure", plan: "Annually / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 3, a: 3 }, mar: { p: 0, a: 3 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 37, name: "Review RADAR Observation", plan: "Monthly / Base", responsible: "Manager/Supv", progress: 92, monthly: { jan: { p: 3, a: 3 }, feb: { p: 3, a: 3 }, mar: { p: 3, a: 3 }, apr: { p: 3, a: 3 }, may: { p: 3, a: 3 }, jun: { p: 3, a: 3 }, jul: { p: 3, a: 3 }, aug: { p: 3, a: 3 }, sep: { p: 3, a: 3 }, oct: { p: 3, a: 3 }, nov: { p: 3, a: 3 }, dec: { p: 3, a: 0 } } },
                        { id: 38, name: "Provide HSE Campaign Banner", plan: "Quarterly / Base", responsible: "Facility Supv", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 1, a: 1 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 1, a: 1 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 1, a: 1 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 1, a: 1 }, dec: { p: 0, a: 0 } } },
                        { id: 39, name: "Conduct Emergency Drill", plan: "Quarterly / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 1, a: 2 }, feb: { p: 1, a: 3 }, mar: { p: 1, a: 3 }, apr: { p: 1, a: 3 }, may: { p: 1, a: 1 }, jun: { p: 1, a: 1 }, jul: { p: 1, a: 1 }, aug: { p: 1, a: 2 }, sep: { p: 1, a: 1 }, oct: { p: 1, a: 1 }, nov: { p: 1, a: 1 }, dec: { p: 1, a: 0 } } }
                    ]
                },
                {
                    id: 6,
                    name: "Minimize Incident with Lifting Equipment",
                    target: "Zero Serious Injury and Fatality (SIF)",
                    programs: [
                        { id: 40, name: "Conduct Lifting gear inspection", plan: "Per Semester", responsible: "Third Party", progress: 100, monthly: { jan: { p: 1, a: 1 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 1, a: 1 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 41, name: "Lifting Gear Inspection report", plan: "Monthly / Base", responsible: "Supv", progress: 92, monthly: { jan: { p: 3, a: 3 }, feb: { p: 3, a: 3 }, mar: { p: 3, a: 3 }, apr: { p: 3, a: 3 }, may: { p: 3, a: 3 }, jun: { p: 3, a: 3 }, jul: { p: 3, a: 3 }, aug: { p: 3, a: 3 }, sep: { p: 3, a: 3 }, oct: { p: 3, a: 3 }, nov: { p: 3, a: 3 }, dec: { p: 3, a: 0 } } },
                        { id: 42, name: "SQM Meeting with TMC crane supplier", plan: "Annually", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 1, a: 1 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 43, name: "Lifting Awareness Campaign", plan: "Annually / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 3, a: 3 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 44, name: "Refresh Mechanical Lifting SWC Training", plan: "Annually / Base", responsible: "HSE", progress: 67, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 1, a: 1 }, aug: { p: 1, a: 1 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 1, a: 0 } } },
                        { id: 45, name: "Lifting Equipment Standard Audit", plan: "Annually / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 1, a: 1 }, aug: { p: 1, a: 1 }, sep: { p: 0, a: 0 }, oct: { p: 1, a: 1 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } }
                    ]
                },
                {
                    id: 7,
                    name: "Minimize Impact from Hazardous Substance",
                    target: "Zero Environmental Incident",
                    programs: [
                        { id: 46, name: "Review Chemical MSDS", plan: "Annually / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 1, a: 1 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 1, a: 1 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 1, a: 1 }, dec: { p: 0, a: 0 } } },
                        { id: 47, name: "Conduct Monthly waste water analysis", plan: "Monthly / Base", responsible: "HSE", progress: 92, monthly: { jan: { p: 3, a: 3 }, feb: { p: 3, a: 3 }, mar: { p: 3, a: 3 }, apr: { p: 3, a: 3 }, may: { p: 3, a: 3 }, jun: { p: 3, a: 3 }, jul: { p: 3, a: 3 }, aug: { p: 3, a: 3 }, sep: { p: 3, a: 3 }, oct: { p: 3, a: 3 }, nov: { p: 3, a: 3 }, dec: { p: 3, a: 0 } } },
                        { id: 48, name: "Conduct Environmental Monitoring", plan: "Per Semester / Base", responsible: "HSE", progress: 50, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 3, a: 3 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 3, a: 0 } } },
                        { id: 49, name: "Dispose Hazardous waste", plan: "Per Semester / Base", responsible: "Facility Supv", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 1, a: 1 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 1, a: 1 }, dec: { p: 0, a: 0 } } },
                        { id: 50, name: "Conduct Industrial Hygiene Test", plan: "Annually / Base", responsible: "Facility", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 3, a: 3 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 51, name: "Indonesia Environment Improvement Plan", plan: "Annual report/year", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 1, a: 1 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 52, name: "Conduct Emergency Spill Drill", plan: "Annually / Base", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 1, a: 1 }, mar: { p: 1, a: 1 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } }
                    ]
                },
                {
                    id: 8,
                    name: "Minimize Health Risk and Improve Awareness",
                    target: "Zero Health Case / Incident",
                    programs: [
                        { id: 53, name: "Conduct Medical Check-Up", plan: "Annually", responsible: "Manager/Supv", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 1, a: 1 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 54, name: "Drug and Alcohol test", plan: "Annually", responsible: "Manager/Supv", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 1, a: 1 }, mar: { p: 0, a: 0 }, apr: { p: 0, a: 0 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } },
                        { id: 55, name: "Conduct Health Campaign", plan: "Per Semester", responsible: "HSE", progress: 100, monthly: { jan: { p: 0, a: 0 }, feb: { p: 0, a: 0 }, mar: { p: 0, a: 0 }, apr: { p: 2, a: 2 }, may: { p: 0, a: 0 }, jun: { p: 0, a: 0 }, jul: { p: 0, a: 0 }, aug: { p: 0, a: 0 }, sep: { p: 0, a: 0 }, oct: { p: 0, a: 0 }, nov: { p: 0, a: 0 }, dec: { p: 0, a: 0 } } }
                    ]
                }
            ]
        },
        2024: { objectives: [] },
        2026: { objectives: [] }
    };

    function selectOTPYear(year) {
        selectedOTPYear = parseInt(year);
        document.getElementById('otp-year-title').textContent = year + ' HSE OTP';
        renderOTPScreen();
    }

    function filterOTPByMonth(month) {
        selectedOTPMonth = month;
        var btns = document.querySelectorAll('.otp-month-filter');
        for (var i = 0; i < btns.length; i++) {
            var btn = btns[i];
            var isActive = btn.dataset.month === month;
            btn.style.background = isActive ? 'var(--netflix-red)' : 'var(--bg-tertiary)';
            btn.style.color = isActive ? 'white' : 'var(--text-primary)';
            btn.style.border = isActive ? 'none' : '1px solid var(--border)';
        }
        renderOTPScreen();
    }

    function toggleOTPObjective(id) {
        var content = document.getElementById('otp-obj-content-' + id);
        var arrow = document.getElementById('otp-obj-arrow-' + id);
        if (content && arrow) {
            var isHidden = content.style.display === 'none';
            content.style.display = isHidden ? 'block' : 'none';
            arrow.textContent = isHidden ? '▼' : '▶';
        }
    }

    function getOTPMonthStatus(monthData) {
        if (!monthData || typeof monthData !== 'object') return { dot: '⚪', text: '0/0' };
        var plan = monthData.p || 0;
        var actual = monthData.a || 0;
        if (plan === 0 && actual === 0) return { dot: '⚪', text: '0/0' };
        if (actual >= plan) return { dot: '🟢', text: actual + '/' + plan };
        if (actual > 0) return { dot: '🟡', text: actual + '/' + plan };
        return { dot: '🔴', text: actual + '/' + plan };
    }

    function renderOTPScreen() {
        var yearData = otpData[selectedOTPYear] || { objectives: [] };
        var objectives = yearData.objectives || [];

        var total = 0, complete = 0, inProgress = 0, notStarted = 0;
        for (var i = 0; i < objectives.length; i++) {
            var obj = objectives[i];
            for (var j = 0; j < obj.programs.length; j++) {
                var p = obj.programs[j];
                total++;
                if (p.progress >= 100) complete++;
                else if (p.progress > 0) inProgress++;
                else notStarted++;
            }
        }

        document.getElementById('otp-summary-cards').innerHTML =
            '<div style="background: linear-gradient(135deg, #3498db, #2980b9); border-radius: 12px; padding: 16px; text-align: center;"><div style="font-size: 28px; font-weight: 700; color: white;">' + total + '</div><div style="font-size: 11px; color: rgba(255,255,255,0.8);">Total Programs</div></div>' +
            '<div style="background: linear-gradient(135deg, #27ae60, #2ecc71); border-radius: 12px; padding: 16px; text-align: center;"><div style="font-size: 28px; font-weight: 700; color: white;">' + complete + '</div><div style="font-size: 11px; color: rgba(255,255,255,0.8);">Complete</div></div>' +
            '<div style="background: linear-gradient(135deg, #f39c12, #e67e22); border-radius: 12px; padding: 16px; text-align: center;"><div style="font-size: 28px; font-weight: 700; color: white;">' + inProgress + '</div><div style="font-size: 11px; color: rgba(255,255,255,0.8);">In Progress</div></div>' +
            '<div style="background: linear-gradient(135deg, #e74c3c, #c0392b); border-radius: 12px; padding: 16px; text-align: center;"><div style="font-size: 28px; font-weight: 700; color: white;">' + notStarted + '</div><div style="font-size: 11px; color: rgba(255,255,255,0.8);">Not Started</div></div>';

        var objHtml = '';
        var months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];

        for (var i = 0; i < objectives.length; i++) {
            var obj = objectives[i];
            var progHtml = '';

            for (var j = 0; j < obj.programs.length; j++) {
                var p = obj.programs[j];
                var monthDots = '';

                for (var k = 0; k < months.length; k++) {
                    var m = months[k];
                    var monthData = p.monthly[m] || { p: 0, a: 0 };
                    var status = getOTPMonthStatus(monthData);
                    if (selectedOTPMonth !== 'all' && m !== selectedOTPMonth) continue;
                    monthDots += '<span title="' + m.toUpperCase() + ': ' + status.text + '" style="font-size: 10px;">' + status.dot + '</span>';
                }

                var progressColor = p.progress >= 100 ? '#27ae60' : (p.progress > 0 ? '#f39c12' : '#e74c3c');
                progHtml += '<div style="background: var(--bg-tertiary); border-radius: 10px; padding: 14px; margin-bottom: 10px;"><div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;"><div style="flex: 1;"><div style="font-weight: 600; font-size: 13px; color: var(--text-primary); margin-bottom: 4px;">' + p.id + '. ' + p.name + '</div><div style="font-size: 11px; color: var(--text-muted);">📅 ' + p.plan + ' 👤 ' + p.responsible + '</div></div><div style="font-size: 14px; font-weight: 700; color: ' + progressColor + ';">' + p.progress + '%</div></div><div style="background: var(--bg-primary); border-radius: 4px; height: 6px; overflow: hidden; margin-bottom: 8px;"><div style="background: ' + progressColor + '; height: 100%; width: ' + p.progress + '%;"></div></div><div style="display: flex; gap: 3px; flex-wrap: wrap;">' + monthDots + '</div></div>';
            }

            objHtml += '<div style="background: var(--bg-secondary); border-radius: 12px; margin-bottom: 16px; overflow: hidden;"><div onclick="toggleOTPObjective(' + obj.id + ')" style="padding: 16px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #e50914, #b20710);"><div><div style="font-weight: 700; font-size: 14px; color: white;">OBJECTIVE ' + obj.id + ': ' + obj.name + '</div><div style="font-size: 12px; color: rgba(255,255,255,0.8); margin-top: 4px;">Target: ' + obj.target + '</div></div><span id="otp-obj-arrow-' + obj.id + '" style="color: white; font-size: 16px;">▼</span></div><div id="otp-obj-content-' + obj.id + '" style="padding: 16px;">' + progHtml + '</div></div>';
        }

        document.getElementById('otp-objectives-container').innerHTML = objHtml || '<div style="text-align: center; color: var(--text-muted); padding: 40px;">No programs for this year</div>';
    }

    // Expose functions globally
    window.selectOTPYear = selectOTPYear;
    window.filterOTPByMonth = filterOTPByMonth;
    window.toggleOTPObjective = toggleOTPObjective;
    window.renderOTPScreen = renderOTPScreen;
})();
