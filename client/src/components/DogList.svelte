<script lang="ts">
    import { onMount } from "svelte";
    import FilterPanel from "./FilterPanel.svelte";

    interface Dog {
        id: number;
        name: string;
        breed: string;
        age: number;
        gender: string;
        status: string;
    }

    interface FilterState {
        search: string;
        breeds: string[];
        ageRange: string;
        gender: string;
        status: string;
    }

    let dogs: Dog[] = $state([]);
    let loading = $state(true);
    let error: string | null = $state(null);
    let totalCount = $state(0);

    const ageRanges: Record<string, { min: number | null; max: number | null }> = {
        'all': { min: null, max: null },
        'puppy': { min: 0, max: 1 },
        'young': { min: 1, max: 3 },
        'adult': { min: 3, max: 7 },
        'senior': { min: 7, max: null }
    };

    const fetchDogs = async (filters?: FilterState) => {
        loading = true;
        error = null;
        
        try {
            const params = new URLSearchParams();
            
            if (filters) {
                if (filters.search) {
                    params.set('search', filters.search);
                }
                
                if (filters.breeds.length > 0) {
                    params.set('breed', filters.breeds.join(','));
                }
                
                if (filters.ageRange && filters.ageRange !== 'all') {
                    const range = ageRanges[filters.ageRange];
                    if (range.min !== null) params.set('age_min', range.min.toString());
                    if (range.max !== null) params.set('age_max', range.max.toString());
                }
                
                if (filters.gender && filters.gender !== 'Any') {
                    params.set('gender', filters.gender);
                }
                
                if (filters.status) {
                    params.set('status', filters.status);
                }
            } else {
                // Default filter: show only available dogs
                params.set('status', 'AVAILABLE');
            }

            const queryString = params.toString();
            const url = queryString ? `/api/dogs?${queryString}` : '/api/dogs';
            
            const response = await fetch(url);
            if(response.ok) {
                const data = await response.json();
                dogs = data.dogs || [];
                totalCount = data.total || 0;
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    function handleFilterChange(filters: FilterState) {
        fetchDogs(filters);
    }

    onMount(() => {
        // Initial load will be handled by FilterPanel's URL parsing
        const params = new URLSearchParams(window.location.search);
        const hasFilters = params.toString().length > 0;
        
        if (!hasFilters) {
            // Default to showing available dogs
            fetchDogs({ search: '', breeds: [], ageRange: 'all', gender: 'Any', status: 'AVAILABLE' });
        }
    });
</script>

<div>
    <h2 class="text-2xl font-medium mb-6 text-slate-100">Available Dogs</h2>
    
    <FilterPanel 
        onFilterChange={handleFilterChange}
        dogCount={dogs.length}
        totalCount={totalCount}
    />
    
    {#if loading}
        <!-- loading animation -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _, i}
                <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50">
                    <div class="p-6">
                        <div class="animate-pulse">
                            <div class="h-6 bg-slate-700 rounded w-3/4 mb-3"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/2 mb-4"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/4 mt-6"></div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if error}
        <!-- error display -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-red-400">{error}</p>
        </div>
    {:else if dogs.length === 0}
        <!-- no dogs found -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h3 class="text-xl font-semibold text-slate-300 mb-2">No dogs match your search criteria</h3>
            <p class="text-slate-400 mb-6">Try adjusting your filters to see more results</p>
        </div>
    {:else}
        <!-- dog list -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each dogs as dog (dog.id)}
                <a 
                    href={`/dog/${dog.id}`} 
                    class="group block bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50 hover:border-blue-500/50 hover:shadow-blue-500/10 hover:shadow-xl transition-all duration-300 hover:translate-y-[-6px]"
                >
                    <div class="p-6 relative">
                        <div class="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div class="relative z-10">
                            <div class="flex items-start justify-between mb-2">
                                <h3 class="text-xl font-semibold text-slate-100 group-hover:text-blue-400 transition-colors">{dog.name}</h3>
                                {#if dog.status === 'AVAILABLE'}
                                    <span class="px-2 py-1 bg-green-500/20 text-green-400 text-xs font-medium rounded-full">Available</span>
                                {:else if dog.status === 'PENDING'}
                                    <span class="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs font-medium rounded-full">Pending</span>
                                {:else if dog.status === 'ADOPTED'}
                                    <span class="px-2 py-1 bg-gray-500/20 text-gray-400 text-xs font-medium rounded-full">Adopted</span>
                                {/if}
                            </div>
                            <p class="text-slate-400 mb-2">{dog.breed}</p>
                            <div class="flex items-center gap-4 text-sm text-slate-500 mb-4">
                                <span>{dog.age} {dog.age === 1 ? 'year' : 'years'} old</span>
                                <span>•</span>
                                <span>{dog.gender}</span>
                            </div>
                            <div class="mt-4 text-sm text-blue-400 font-medium flex items-center">
                                <span>View details</span>
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 transform transition-transform duration-300 group-hover:translate-x-2" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </a>
            {/each}
        </div>
    {/if}
</div>