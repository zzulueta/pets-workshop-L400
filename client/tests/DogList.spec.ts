import { render, waitFor } from '@testing-library/svelte';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import DogList from '../src/components/DogList.svelte';

/**
 * Test suite for DogList component
 * Tests rendering, API integration, dog cards, error handling, and accessibility
 */
describe('DogList Component', () => {
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
        it('should render loading state with skeleton cards', () => {
            const { container } = render(DogList);
            
            const skeletonCards = container.querySelectorAll('.animate-pulse');
            expect(skeletonCards.length).toBeGreaterThan(0);
            
            // Should render 6 skeleton cards
            const loadingCards = container.querySelectorAll('.bg-slate-800\\/60');
            expect(loadingCards.length).toBe(6);
        });

        it('should render error state when fetch fails', async () => {
            (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

            const { getByText } = render(DogList);

            await waitFor(() => {
                expect(getByText(/Error: Network error/i)).toBeTruthy();
            });
        });

        it('should render empty state when no dogs available', async () => {
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => []
            });

            const { getByText } = render(DogList);

            await waitFor(() => {
                expect(getByText(/No dogs available at the moment/i)).toBeTruthy();
            });
        });

        it('should render dog list with correct data', async () => {
            const mockDogs = [
                { id: 1, name: 'Buddy', breed: 'Golden Retriever' },
                { id: 2, name: 'Max', breed: 'Labrador' },
                { id: 3, name: 'Luna', breed: 'Husky' }
            ];

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockDogs
            });

            const { getByText } = render(DogList);

            await waitFor(() => {
                expect(getByText('Buddy')).toBeTruthy();
                expect(getByText('Golden Retriever')).toBeTruthy();
                expect(getByText('Max')).toBeTruthy();
                expect(getByText('Labrador')).toBeTruthy();
                expect(getByText('Luna')).toBeTruthy();
                expect(getByText('Husky')).toBeTruthy();
            });
        });
    });

    /**
     * Test Suite: Dog Cards
     */
    describe('Dog Cards', () => {
        it('should link each dog card to correct detail page', async () => {
            const mockDogs = [
                { id: 1, name: 'Buddy', breed: 'Golden Retriever' },
                { id: 2, name: 'Max', breed: 'Labrador' },
                { id: 3, name: 'Luna', breed: 'Husky' }
            ];

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockDogs
            });

            const { container } = render(DogList);

            await waitFor(() => {
                const links = container.querySelectorAll('a[href^="/dog/"]');
                expect(links.length).toBe(3);
                expect(links[0].getAttribute('href')).toBe('/dog/1');
                expect(links[1].getAttribute('href')).toBe('/dog/2');
                expect(links[2].getAttribute('href')).toBe('/dog/3');
            });
        });

        it('should display correct content in dog cards', async () => {
            const mockDogs = [
                { id: 1, name: 'Buddy', breed: 'Golden Retriever' }
            ];

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockDogs
            });

            const { container, getByText } = render(DogList);

            await waitFor(() => {
                expect(getByText('Buddy')).toBeTruthy();
                expect(getByText('Golden Retriever')).toBeTruthy();
                expect(getByText('View details')).toBeTruthy();
            });

            const card = container.querySelector('a[href="/dog/1"]');
            expect(card).toBeTruthy();
        });

        it('should have hover effects CSS classes on dog cards', async () => {
            const mockDogs = [
                { id: 1, name: 'Buddy', breed: 'Golden Retriever' }
            ];

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockDogs
            });

            const { container } = render(DogList);

            await waitFor(() => {
                const card = container.querySelector('a[href="/dog/1"]');
                expect(card?.classList.contains('group')).toBe(true);
                expect(card?.className).toContain('hover:border-blue-500');
                expect(card?.className).toContain('hover:translate-y-[-6px]');
            });
        });

        it('should render all dogs with unique keys', async () => {
            const mockDogs = [
                { id: 1, name: 'Buddy', breed: 'Golden Retriever' },
                { id: 2, name: 'Max', breed: 'Labrador' },
                { id: 3, name: 'Luna', breed: 'Husky' },
                { id: 4, name: 'Charlie', breed: 'Beagle' }
            ];

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockDogs
            });

            const { container } = render(DogList);

            await waitFor(() => {
                const cards = container.querySelectorAll('a[href^="/dog/"]');
                expect(cards.length).toBe(4);
            });
        });
    });

    /**
     * Test Suite: API Integration
     */
    describe('API Integration', () => {
        it('should fetch dogs from correct endpoint', async () => {
            const mockDogs = [
                { id: 1, name: 'Buddy', breed: 'Golden Retriever' }
            ];

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockDogs
            });

            render(DogList);

            await waitFor(() => {
                expect(global.fetch).toHaveBeenCalledWith('/api/dogs');
            });
        });

        it('should handle network errors gracefully', async () => {
            (global.fetch as any).mockRejectedValueOnce(new Error('Failed to fetch'));

            const { getByText } = render(DogList);

            await waitFor(() => {
                expect(getByText(/Error: Failed to fetch/i)).toBeTruthy();
            });
        });

        it('should handle 404 response code', async () => {
            (global.fetch as any).mockResolvedValueOnce({
                ok: false,
                status: 404,
                statusText: 'Not Found'
            });

            const { getByText } = render(DogList);

            await waitFor(() => {
                expect(getByText(/Failed to fetch data: 404 Not Found/i)).toBeTruthy();
            });
        });

        it('should handle 500 response code', async () => {
            (global.fetch as any).mockResolvedValueOnce({
                ok: false,
                status: 500,
                statusText: 'Internal Server Error'
            });

            const { getByText } = render(DogList);

            await waitFor(() => {
                expect(getByText(/Failed to fetch data: 500 Internal Server Error/i)).toBeTruthy();
            });
        });

        it('should handle malformed JSON response', async () => {
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => {
                    throw new Error('Invalid JSON');
                }
            });

            const { getByText } = render(DogList);

            await waitFor(() => {
                expect(getByText(/Error: Invalid JSON/i)).toBeTruthy();
            });
        });
    });

    /**
     * Test Suite: Accessibility
     */
    describe('Accessibility', () => {
        it('should have keyboard navigable dog cards', async () => {
            const mockDogs = [
                { id: 1, name: 'Buddy', breed: 'Golden Retriever' },
                { id: 2, name: 'Max', breed: 'Labrador' }
            ];

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockDogs
            });

            const { container } = render(DogList);

            await waitFor(() => {
                const links = container.querySelectorAll('a[href^="/dog/"]');
                expect(links.length).toBe(2);
                
                // All cards should be anchor elements (focusable)
                links.forEach((link: Element) => {
                    expect(link.tagName.toLowerCase()).toBe('a');
                });
            });
        });

        it('should have correct heading hierarchy', async () => {
            const { container } = render(DogList);

            const heading = container.querySelector('h2');
            expect(heading).toBeTruthy();
            expect(heading?.textContent).toContain('Available Dogs');
        });

        it('should have semantic HTML structure', async () => {
            const mockDogs = [
                { id: 1, name: 'Buddy', breed: 'Golden Retriever' }
            ];

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockDogs
            });

            const { container } = render(DogList);

            await waitFor(() => {
                const heading = container.querySelector('h3');
                expect(heading).toBeTruthy();
                expect(heading?.textContent).toBe('Buddy');
            });
        });
    });

    /**
     * Test Suite: Loading State
     */
    describe('Loading State', () => {
        it('should show loading state initially', () => {
            const { container } = render(DogList);
            
            const loadingElement = container.querySelector('.animate-pulse');
            expect(loadingElement).toBeTruthy();
        });

        it('should hide loading state after successful fetch', async () => {
            const mockDogs = [
                { id: 1, name: 'Buddy', breed: 'Golden Retriever' }
            ];

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockDogs
            });

            const { container } = render(DogList);

            await waitFor(() => {
                const loadingSkeletons = container.querySelectorAll('.animate-pulse');
                expect(loadingSkeletons.length).toBe(0);
            });
        });

        it('should hide loading state after error', async () => {
            (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

            const { container } = render(DogList);

            await waitFor(() => {
                const loadingElement = container.querySelector('.animate-pulse');
                expect(loadingElement).toBeFalsy();
            });
        });
    });

    /**
     * Test Suite: Grid Layout
     */
    describe('Grid Layout', () => {
        it('should use grid layout for dog cards', async () => {
            const mockDogs = [
                { id: 1, name: 'Buddy', breed: 'Golden Retriever' },
                { id: 2, name: 'Max', breed: 'Labrador' }
            ];

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockDogs
            });

            const { container } = render(DogList);

            await waitFor(() => {
                const grid = container.querySelector('.grid');
                expect(grid).toBeTruthy();
                expect(grid?.className).toContain('grid-cols-1');
                expect(grid?.className).toContain('sm:grid-cols-2');
                expect(grid?.className).toContain('lg:grid-cols-3');
            });
        });
    });
});
