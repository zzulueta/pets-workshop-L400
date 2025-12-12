<script lang="ts">
    import { onMount } from "svelte";

    interface FilterState {
        search: string;
        breeds: string[];
        ageRange: string;
        gender: string;
        status: string;
    }

    interface Props {
        onFilterChange: (filters: FilterState) => void;
        dogCount?: number;
        totalCount?: number;
    }

    let { onFilterChange, dogCount = 0, totalCount = 0 }: Props = $props();

    let filters: FilterState = $state({
        search: '',
        breeds: [],
        ageRange: 'all',
        gender: 'Any',
        status: 'AVAILABLE'
    });

    let availableBreeds: string[] = $state([]);
    let showFilters = $state(true);
    let searchTimeout: number | undefined;

    const ageRanges = [
        { value: 'all', label: 'All Ages', min: null, max: null },
        { value: 'puppy', label: 'Puppy (0-1 years)', min: 0, max: 1 },
        { value: 'young', label: 'Young (1-3 years)', min: 1, max: 3 },
        { value: 'adult', label: 'Adult (3-7 years)', min: 3, max: 7 },
        { value: 'senior', label: 'Senior (7+ years)', min: 7, max: null }
    ];

    const genderOptions = ['Any', 'Male', 'Female', 'Unknown'];
    const statusOptions = [
        { value: 'AVAILABLE', label: 'Available' },
        { value: 'PENDING', label: 'Pending' },
        { value: 'ADOPTED', label: 'Adopted' },
        { value: 'ALL', label: 'All Status' }
    ];

    onMount(async () => {
        await fetchBreeds();
        loadFiltersFromURL();
    });

    async function fetchBreeds() {
        try {
            const response = await fetch('/api/breeds');
            if (response.ok) {
                availableBreeds = await response.json();
            }
        } catch (err) {
            console.error('Error fetching breeds:', err);
        }
    }

    function loadFiltersFromURL() {
        const params = new URLSearchParams(window.location.search);
        const search = params.get('search') || '';
        const breedParam = params.get('breed') || '';
        const breeds = breedParam ? breedParam.split(',') : [];
        const ageRange = params.get('ageRange') || 'all';
        const gender = params.get('gender') || 'Any';
        const status = params.get('status') || 'AVAILABLE';

        filters = { search, breeds, ageRange, gender, status };
        notifyFilterChange();
    }

    function updateURL() {
        const params = new URLSearchParams();
        
        if (filters.search) params.set('search', filters.search);
        if (filters.breeds.length > 0) params.set('breed', filters.breeds.join(','));
        if (filters.ageRange !== 'all') params.set('ageRange', filters.ageRange);
        if (filters.gender !== 'Any') params.set('gender', filters.gender);
        if (filters.status !== 'AVAILABLE') params.set('status', filters.status);

        const newURL = params.toString() ? `?${params.toString()}` : window.location.pathname;
        window.history.replaceState({}, '', newURL);
    }

    function notifyFilterChange() {
        updateURL();
        onFilterChange(filters);
    }

    function handleSearchInput(event: Event) {
        const target = event.target as HTMLInputElement;
        filters.search = target.value;
        
        // Debounce search input
        clearTimeout(searchTimeout);
        searchTimeout = window.setTimeout(() => {
            notifyFilterChange();
        }, 300);
    }

    function handleBreedChange(breed: string) {
        if (filters.breeds.includes(breed)) {
            filters.breeds = filters.breeds.filter(b => b !== breed);
        } else {
            filters.breeds = [...filters.breeds, breed];
        }
        notifyFilterChange();
    }

    function handleAgeRangeChange(event: Event) {
        const target = event.target as HTMLSelectElement;
        filters.ageRange = target.value;
        notifyFilterChange();
    }

    function handleGenderChange(event: Event) {
        const target = event.target as HTMLSelectElement;
        filters.gender = target.value;
        notifyFilterChange();
    }

    function handleStatusChange(event: Event) {
        const target = event.target as HTMLSelectElement;
        filters.status = target.value;
        notifyFilterChange();
    }

    function clearAllFilters() {
        filters = {
            search: '',
            breeds: [],
            ageRange: 'all',
            gender: 'Any',
            status: 'AVAILABLE'
        };
        notifyFilterChange();
    }

    function hasActiveFilters(): boolean {
        return filters.search !== '' ||
               filters.breeds.length > 0 ||
               filters.ageRange !== 'all' ||
               filters.gender !== 'Any' ||
               filters.status !== 'AVAILABLE';
    }

    function getActiveFilterCount(): number {
        let count = 0;
        if (filters.search) count++;
        if (filters.breeds.length > 0) count += filters.breeds.length;
        if (filters.ageRange !== 'all') count++;
        if (filters.gender !== 'Any') count++;
        if (filters.status !== 'AVAILABLE') count++;
        return count;
    }
</script>

<div class="mb-8">
    <!-- Filter Header -->
    <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-3">
            <h3 class="text-xl font-semibold text-slate-100">Filter Dogs</h3>
            {#if hasActiveFilters()}
                <span class="px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm font-medium">
                    {getActiveFilterCount()} active
                </span>
            {/if}
        </div>
        <button
            onclick={() => showFilters = !showFilters}
            class="md:hidden px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-100 rounded-lg transition-colors"
            aria-label={showFilters ? 'Hide filters' : 'Show filters'}
        >
            {showFilters ? 'Hide' : 'Show'} Filters
        </button>
    </div>

    <!-- Results Count -->
    <div class="mb-4 text-slate-300">
        Showing <span class="font-semibold text-slate-100">{dogCount}</span> of <span class="font-semibold text-slate-100">{totalCount}</span> dogs
    </div>

    <!-- Filter Panel -->
    <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50" class:hidden={!showFilters}>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <!-- Search Input -->
            <div class="lg:col-span-2">
                <label for="search" class="block text-sm font-medium text-slate-300 mb-2">
                    Search by Name or Breed
                </label>
                <input
                    id="search"
                    type="text"
                    value={filters.search}
                    oninput={handleSearchInput}
                    placeholder="e.g., Buddy, Labrador..."
                    class="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>

            <!-- Age Range -->
            <div>
                <label for="ageRange" class="block text-sm font-medium text-slate-300 mb-2">
                    Age Range
                </label>
                <select
                    id="ageRange"
                    value={filters.ageRange}
                    onchange={handleAgeRangeChange}
                    class="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                    {#each ageRanges as range}
                        <option value={range.value}>{range.label}</option>
                    {/each}
                </select>
            </div>

            <!-- Gender -->
            <div>
                <label for="gender" class="block text-sm font-medium text-slate-300 mb-2">
                    Gender
                </label>
                <select
                    id="gender"
                    value={filters.gender}
                    onchange={handleGenderChange}
                    class="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                    {#each genderOptions as genderOption}
                        <option value={genderOption}>{genderOption}</option>
                    {/each}
                </select>
            </div>

            <!-- Status -->
            <div>
                <label for="status" class="block text-sm font-medium text-slate-300 mb-2">
                    Status
                </label>
                <select
                    id="status"
                    value={filters.status}
                    onchange={handleStatusChange}
                    class="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                    {#each statusOptions as statusOption}
                        <option value={statusOption.value}>{statusOption.label}</option>
                    {/each}
                </select>
            </div>
        </div>

        <!-- Breed Multi-Select -->
        {#if availableBreeds.length > 0}
            <div class="mt-4">
                <label class="block text-sm font-medium text-slate-300 mb-2">
                    Breeds (select multiple)
                </label>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 max-h-48 overflow-y-auto p-2 bg-slate-700/50 rounded-lg">
                    {#each availableBreeds as breed}
                        <label class="flex items-center space-x-2 cursor-pointer hover:bg-slate-600/50 p-2 rounded transition-colors">
                            <input
                                type="checkbox"
                                checked={filters.breeds.includes(breed)}
                                onchange={() => handleBreedChange(breed)}
                                class="w-4 h-4 text-blue-500 bg-slate-600 border-slate-500 rounded focus:ring-2 focus:ring-blue-500"
                            />
                            <span class="text-sm text-slate-200">{breed}</span>
                        </label>
                    {/each}
                </div>
            </div>
        {/if}

        <!-- Clear Filters Button -->
        {#if hasActiveFilters()}
            <div class="mt-4 flex justify-end">
                <button
                    onclick={clearAllFilters}
                    class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-100 rounded-lg transition-colors flex items-center gap-2"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                    Clear All Filters
                </button>
            </div>
        {/if}
    </div>
</div>
