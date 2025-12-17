import { render, waitFor } from '@testing-library/svelte';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import DogDetails from '../src/components/DogDetails.svelte';

/**
 * Test suite for DogDetails component
 * Tests rendering, API integration, status badges, human age feature, and accessibility
 */
describe('DogDetails Component', () => {
    beforeEach(() => {
        // Reset fetch mock before each test
        global.fetch = vi.fn();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    /**
     * Test Suite: Component Rendering
     */
    describe('Component Rendering', () => {
        it('should render loading state correctly', () => {
            const { container } = render(DogDetails, { props: { dogId: 1 } });
            
            const loadingElement = container.querySelector('.animate-pulse');
            expect(loadingElement).toBeTruthy();
            expect(container.querySelector('.bg-slate-700')).toBeTruthy();
        });

        it('should render error state when fetch fails', async () => {
            (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

            const { getByText } = render(DogDetails, { props: { dogId: 1 } });

            await waitFor(() => {
                expect(getByText(/Error: Network error/i)).toBeTruthy();
            });
        });

        it('should render error state when no dog ID provided', async () => {
            const { getByText } = render(DogDetails, { props: {} });

            await waitFor(() => {
                expect(getByText(/No dog ID provided/i)).toBeTruthy();
            });
        });

        it('should render dog data when provided directly via prop', async () => {
            const mockDog = {
                id: 1,
                name: 'Buddy',
                breed: 'Golden Retriever',
                age: 3,
                description: 'A friendly dog',
                gender: 'Male',
                status: 'AVAILABLE' as const
            };

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ dog_name: 'Buddy', dog_age: 3, human_age: 28 })
            });

            const { getByText } = render(DogDetails, { props: { dog: mockDog } });

            await waitFor(() => {
                expect(getByText('Buddy')).toBeTruthy();
                expect(getByText(/Golden Retriever/i)).toBeTruthy();
                expect(getByText(/3 years/i)).toBeTruthy();
                expect(getByText(/Male/i)).toBeTruthy();
                expect(getByText('A friendly dog')).toBeTruthy();
            });
        });

        it('should fetch and render dog data when dogId provided', async () => {
            const mockDog = {
                id: 1,
                name: 'Max',
                breed: 'Labrador',
                age: 5,
                description: 'Energetic and playful',
                gender: 'Male',
                status: 'AVAILABLE' as const
            };

            (global.fetch as any)
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => mockDog
                })
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ dog_name: 'Max', dog_age: 5, human_age: 40 })
                });

            const { getByText } = render(DogDetails, { props: { dogId: 1 } });

            await waitFor(() => {
                expect(getByText('Max')).toBeTruthy();
                expect(getByText(/Labrador/i)).toBeTruthy();
            });

            expect(global.fetch).toHaveBeenCalledWith('/api/dogs/1');
        });
    });

    /**
     * Test Suite: Status Badge Display
     */
    describe('Status Badge Display', () => {
        it('should display Available badge for available dogs', async () => {
            const mockDog = {
                id: 1,
                name: 'Buddy',
                breed: 'Golden Retriever',
                age: 3,
                description: 'A friendly dog',
                gender: 'Male',
                status: 'AVAILABLE' as const
            };

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ dog_name: 'Buddy', dog_age: 3, human_age: 28 })
            });

            const { getByText } = render(DogDetails, { props: { dog: mockDog } });

            await waitFor(() => {
                expect(getByText('Available')).toBeTruthy();
            });
        });

        it('should display Pending Adoption badge for pending dogs', async () => {
            const mockDog = {
                id: 1,
                name: 'Buddy',
                breed: 'Golden Retriever',
                age: 3,
                description: 'A friendly dog',
                gender: 'Male',
                status: 'PENDING' as const
            };

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ dog_name: 'Buddy', dog_age: 3, human_age: 28 })
            });

            const { getByText } = render(DogDetails, { props: { dog: mockDog } });

            await waitFor(() => {
                expect(getByText('Pending Adoption')).toBeTruthy();
            });
        });

        it('should display Adopted badge for adopted dogs', async () => {
            const mockDog = {
                id: 1,
                name: 'Buddy',
                breed: 'Golden Retriever',
                age: 3,
                description: 'A friendly dog',
                gender: 'Male',
                status: 'ADOPTED' as const
            };

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ dog_name: 'Buddy', dog_age: 3, human_age: 28 })
            });

            const { getByText } = render(DogDetails, { props: { dog: mockDog } });

            await waitFor(() => {
                expect(getByText('Adopted')).toBeTruthy();
            });
        });
    });

    /**
     * Test Suite: Human Age Feature
     */
    describe('Human Age Feature', () => {
        it('should fetch and display human age successfully', async () => {
            const mockDog = {
                id: 1,
                name: 'Buddy',
                breed: 'Golden Retriever',
                age: 3,
                description: 'A friendly dog',
                gender: 'Male',
                status: 'AVAILABLE' as const
            };

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ dog_name: 'Buddy', dog_age: 3, human_age: 28 })
            });

            const { getByText } = render(DogDetails, { props: { dog: mockDog } });

            await waitFor(() => {
                expect(getByText(/Human Age:/i)).toBeTruthy();
                expect(getByText(/28 years/i)).toBeTruthy();
            });
        });

        it('should handle human age fetch error gracefully', async () => {
            const mockDog = {
                id: 1,
                name: 'Buddy',
                breed: 'Golden Retriever',
                age: 3,
                description: 'A friendly dog',
                gender: 'Male',
                status: 'AVAILABLE' as const
            };

            (global.fetch as any).mockRejectedValueOnce(new Error('Human age API error'));

            const { container, getByText } = render(DogDetails, { props: { dog: mockDog } });

            await waitFor(() => {
                expect(getByText('Buddy')).toBeTruthy();
            });

            // Human age section should not be displayed
            expect(container.textContent).not.toContain('Human Age:');
        });

        it('should display correct singular year text for age 1', async () => {
            const mockDog = {
                id: 1,
                name: 'Puppy',
                breed: 'Beagle',
                age: 1,
                description: 'Young pup',
                gender: 'Female',
                status: 'AVAILABLE' as const,
                human_age: 15
            };

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ dog_name: 'Puppy', dog_age: 1, human_age: 15 })
            });

            const { getByText } = render(DogDetails, { props: { dog: mockDog } });

            await waitFor(() => {
                expect(getByText(/Age: 1 year/i)).toBeTruthy();
                expect(getByText(/15 years/i)).toBeTruthy();
            });
        });

        it('should display correct plural years text for age greater than 1', async () => {
            const mockDog = {
                id: 1,
                name: 'Buddy',
                breed: 'Golden Retriever',
                age: 5,
                description: 'A friendly dog',
                gender: 'Male',
                status: 'AVAILABLE' as const
            };

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ dog_name: 'Buddy', dog_age: 5, human_age: 40 })
            });

            const { getByText } = render(DogDetails, { props: { dog: mockDog } });

            await waitFor(() => {
                expect(getByText(/Age: 5 years/i)).toBeTruthy();
            });
        });
    });

    /**
     * Test Suite: Accessibility
     */
    describe('Accessibility', () => {
        it('should have proper aria-labels for all dog info sections', async () => {
            const mockDog = {
                id: 1,
                name: 'Buddy',
                breed: 'Golden Retriever',
                age: 3,
                description: 'A friendly dog',
                gender: 'Male',
                status: 'AVAILABLE' as const
            };

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ dog_name: 'Buddy', dog_age: 3, human_age: 28 })
            });

            const { container } = render(DogDetails, { props: { dog: mockDog } });

            await waitFor(() => {
                const breedLabel = container.querySelector('[aria-label="Dog breed"]');
                const ageLabel = container.querySelector('[aria-label="Dog age in years"]');
                const genderLabel = container.querySelector('[aria-label="Dog gender"]');
                
                expect(breedLabel).toBeTruthy();
                expect(ageLabel).toBeTruthy();
                expect(genderLabel).toBeTruthy();
            });

            await waitFor(() => {
                const humanAgeLabel = container.querySelector('[aria-label="Dog age in human years"]');
                expect(humanAgeLabel).toBeTruthy();
            });
        });
    });

    /**
     * Test Suite: API Integration Error Handling
     */
    describe('API Integration Error Handling', () => {
        it('should handle non-200 response codes from dog API', async () => {
            (global.fetch as any).mockResolvedValueOnce({
                ok: false,
                status: 404,
                statusText: 'Not Found'
            });

            const { getByText } = render(DogDetails, { props: { dogId: 999 } });

            await waitFor(() => {
                expect(getByText(/Failed to fetch dog: 404 Not Found/i)).toBeTruthy();
            });
        });

        it('should handle non-200 response codes from human age API', async () => {
            const mockDog = {
                id: 1,
                name: 'Buddy',
                breed: 'Golden Retriever',
                age: 3,
                description: 'A friendly dog',
                gender: 'Male',
                status: 'AVAILABLE' as const
            };

            (global.fetch as any).mockResolvedValueOnce({
                ok: false,
                status: 500,
                statusText: 'Internal Server Error'
            });

            const { getByText, container } = render(DogDetails, { props: { dog: mockDog } });

            await waitFor(() => {
                expect(getByText('Buddy')).toBeTruthy();
            });

            // Component should still render without human age
            expect(container.textContent).not.toContain('Human Age:');
        });
    });
});
