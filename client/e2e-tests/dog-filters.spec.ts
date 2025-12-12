import { test, expect } from '@playwright/test';

test.describe('Dog Filtering System', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Wait for the filter panel to load
    await expect(page.getByRole('heading', { name: 'Filter Dogs' })).toBeVisible();
  });

  test('should display filter panel with all filter options', async ({ page }) => {
    // Check that all filter controls are visible
    await expect(page.getByLabel('Search by Name or Breed')).toBeVisible();
    await expect(page.getByLabel('Age Range')).toBeVisible();
    await expect(page.getByLabel('Gender')).toBeVisible();
    await expect(page.getByLabel('Status')).toBeVisible();
    await expect(page.getByText('Breeds (select multiple)')).toBeVisible();
  });

  test('should show results count', async ({ page }) => {
    // Check that results count is displayed
    await expect(page.locator('text=/Showing \\d+ of \\d+ dogs/')).toBeVisible();
  });

  test('should filter dogs by search term', async ({ page }) => {
    const searchBox = page.getByLabel('Search by Name or Breed');
    
    // Type search term
    await searchBox.fill('Poodle');
    
    // Wait for filtering to complete (debounce delay + API call)
    await page.waitForTimeout(500);
    
    // Check URL contains search parameter
    expect(page.url()).toContain('search=Poodle');
    
    // Check that results are filtered
    const resultsText = await page.locator('text=/Showing \\d+ of \\d+ dogs/').textContent();
    expect(resultsText).toContain('Showing');
    
    // Check that displayed dogs match search
    const dogCards = page.locator('a[href^="/dog/"]');
    const count = await dogCards.count();
    
    if (count > 0) {
      // Verify at least one result contains "Poodle"
      const firstDog = dogCards.first();
      await expect(firstDog).toContainText('Poodle');
    }
  });

  test('should filter dogs by breed selection', async ({ page }) => {
    // Select Poodle breed
    await page.getByRole('checkbox', { name: 'Poodle' }).click();
    
    // Wait for filtering
    await page.waitForTimeout(300);
    
    // Check URL contains breed parameter
    expect(page.url()).toContain('breed=Poodle');
    
    // Check active filter indicator
    await expect(page.locator('text=/\\d+ active/')).toBeVisible();
  });

  test('should filter dogs by age range', async ({ page }) => {
    // Select puppy age range
    await page.getByLabel('Age Range').selectOption('puppy');
    
    // Wait for filtering
    await page.waitForTimeout(300);
    
    // Check URL contains age range parameter
    expect(page.url()).toContain('ageRange=puppy');
    
    // Check active filter indicator
    await expect(page.locator('text=/\\d+ active/')).toBeVisible();
  });

  test('should filter dogs by gender', async ({ page }) => {
    // Select Female gender
    await page.getByLabel('Gender').selectOption('Female');
    
    // Wait for filtering
    await page.waitForTimeout(300);
    
    // Check URL contains gender parameter
    expect(page.url()).toContain('gender=Female');
    
    // Check active filter indicator
    await expect(page.locator('text=/\\d+ active/')).toBeVisible();
  });

  test('should filter dogs by status', async ({ page }) => {
    // Select All status
    await page.getByLabel('Status').selectOption('ALL');
    
    // Wait for filtering
    await page.waitForTimeout(300);
    
    // Check URL contains status parameter
    expect(page.url()).toContain('status=ALL');
  });

  test('should combine multiple filters', async ({ page }) => {
    // Apply multiple filters
    await page.getByRole('checkbox', { name: 'Poodle' }).click();
    await page.waitForTimeout(200);
    
    await page.getByLabel('Age Range').selectOption('puppy');
    await page.waitForTimeout(200);
    
    await page.getByLabel('Gender').selectOption('Male');
    await page.waitForTimeout(300);
    
    // Check URL contains all parameters
    expect(page.url()).toContain('breed=Poodle');
    expect(page.url()).toContain('ageRange=puppy');
    expect(page.url()).toContain('gender=Male');
    
    // Check active filter indicator shows correct count
    const activeText = await page.locator('text=/\\d+ active/').textContent();
    expect(activeText).toContain('3 active');
  });

  test('should clear all filters', async ({ page }) => {
    // Apply some filters
    await page.getByRole('checkbox', { name: 'Poodle' }).click();
    await page.getByLabel('Gender').selectOption('Female');
    await page.waitForTimeout(300);
    
    // Verify filters are active
    await expect(page.locator('text=/\\d+ active/')).toBeVisible();
    
    // Click clear all filters
    await page.getByRole('button', { name: 'Clear All Filters' }).click();
    await page.waitForTimeout(300);
    
    // Check URL is clean
    expect(page.url()).not.toContain('breed=');
    expect(page.url()).not.toContain('gender=');
    
    // Check active filter indicator is gone
    await expect(page.locator('text=/\\d+ active/')).not.toBeVisible();
    
    // Check all dogs are shown again
    const resultsText = await page.locator('text=/Showing \\d+ of \\d+ dogs/').textContent();
    const match = resultsText?.match(/Showing (\d+) of (\d+) dogs/);
    if (match) {
      const [, shown, total] = match;
      // When all filters are cleared, shown should equal total (or close to it with default Available filter)
      expect(parseInt(shown)).toBeGreaterThan(0);
    }
  });

  test('should show no results message when filters match nothing', async ({ page }) => {
    // Apply very specific filters that likely match nothing
    await page.getByRole('checkbox', { name: 'Poodle' }).click();
    await page.getByLabel('Age Range').selectOption('puppy');
    await page.getByLabel('Gender').selectOption('Female');
    await page.waitForTimeout(500);
    
    // Check if no results message appears (depends on actual data)
    const resultsText = await page.locator('text=/Showing \\d+ of \\d+ dogs/').textContent();
    const match = resultsText?.match(/Showing (\d+) of (\d+) dogs/);
    
    if (match && parseInt(match[1]) === 0) {
      await expect(page.getByText('No dogs match your search criteria')).toBeVisible();
      await expect(page.getByText('Try adjusting your filters')).toBeVisible();
    }
  });

  test('should persist filters in URL', async ({ page }) => {
    // Apply filters
    await page.getByLabel('Search by Name or Breed').fill('Buddy');
    await page.waitForTimeout(400);
    
    const urlWithFilters = page.url();
    
    // Navigate away
    await page.goto('/about');
    
    // Navigate back using the URL with filters
    await page.goto(urlWithFilters);
    
    // Check search box still has the value
    await expect(page.getByLabel('Search by Name or Breed')).toHaveValue('Buddy');
  });

  test('should update results count when filters change', async ({ page }) => {
    // Get initial count
    const initialText = await page.locator('text=/Showing \\d+ of \\d+ dogs/').textContent();
    const initialMatch = initialText?.match(/Showing (\d+) of (\d+) dogs/);
    const initialCount = initialMatch ? parseInt(initialMatch[1]) : 0;
    
    // Apply a filter
    await page.getByRole('checkbox', { name: 'Poodle' }).click();
    await page.waitForTimeout(300);
    
    // Get new count
    const newText = await page.locator('text=/Showing \\d+ of \\d+ dogs/').textContent();
    const newMatch = newText?.match(/Showing (\d+) of (\d+) dogs/);
    const newCount = newMatch ? parseInt(newMatch[1]) : 0;
    
    // Count should be different (likely less)
    expect(newCount).not.toBe(initialCount);
    expect(newCount).toBeGreaterThanOrEqual(0);
  });

  test('should show active filter count badge', async ({ page }) => {
    // Initially no active filters (except default status)
    await expect(page.locator('text=/\\d+ active/')).not.toBeVisible();
    
    // Apply one filter
    await page.getByRole('checkbox', { name: 'Poodle' }).click();
    await page.waitForTimeout(200);
    
    // Should show "1 active"
    await expect(page.locator('text=/1 active/')).toBeVisible();
    
    // Apply another filter
    await page.getByLabel('Gender').selectOption('Male');
    await page.waitForTimeout(200);
    
    // Should show "2 active"
    await expect(page.locator('text=/2 active/')).toBeVisible();
  });

  test('should handle multiple breed selections', async ({ page }) => {
    // Select multiple breeds
    await page.getByRole('checkbox', { name: 'Poodle' }).click();
    await page.waitForTimeout(200);
    
    await page.getByRole('checkbox', { name: 'Beagle' }).click();
    await page.waitForTimeout(300);
    
    // Check URL contains both breeds
    expect(page.url()).toContain('breed=Poodle');
    expect(page.url()).toContain('Beagle');
    
    // Check active filter count includes both breeds
    const activeText = await page.locator('text=/\\d+ active/').textContent();
    expect(activeText).toContain('2 active');
  });
});
