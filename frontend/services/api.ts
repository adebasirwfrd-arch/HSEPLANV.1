const API_BASE_URL = 'https://ade-basirwfrd-hseplanv-1.hf.space';

export interface HSEProgram {
    id: number;
    title: string;
    planned_date: string;
    actual_date?: string;
    status: string;
    wpts_number?: string;
    evidence_link?: string;
    manager_email: string;
}

export interface ProgramUpdate {
    actual_date: string;
    status: 'Open' | 'Closed';
    wpts_number: string;
    evidence_link?: string;
}

export interface ProgramCreate {
    title: string;
    planned_date: string;
    manager_email?: string;
}

export const hseApiService = {
    /**
     * Fetch all HSE programs from the backend
     */
    getPrograms: async (): Promise<HSEProgram[]> => {
        const response = await fetch(`${API_BASE_URL}/programs`);
        if (!response.ok) {
            throw new Error('Failed to fetch programs');
        }
        return response.json();
    },

    /**
     * Get a specific HSE program by ID
     */
    getProgram: async (programId: number): Promise<HSEProgram> => {
        const response = await fetch(`${API_BASE_URL}/programs/${programId}`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch program');
        }
        return response.json();
    },

    /**
     * Create a new HSE program
     */
    createProgram: async (programData: ProgramCreate): Promise<HSEProgram> => {
        const response = await fetch(`${API_BASE_URL}/programs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(programData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create program');
        }

        return response.json();
    },

    /**
     * Update an existing HSE program's status
     */
    updateProgram: async (
        programId: number,
        updateData: ProgramUpdate
    ): Promise<HSEProgram> => {
        const response = await fetch(`${API_BASE_URL}/update-program/${programId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updateData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update program');
        }

        return response.json();
    },

    /**
     * Manually trigger reminder check (for testing)
     */
    testReminder: async (): Promise<{ message: string }> => {
        const response = await fetch(`${API_BASE_URL}/test-reminder`, {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error('Failed to trigger reminder');
        }

        return response.json();
    },
};
