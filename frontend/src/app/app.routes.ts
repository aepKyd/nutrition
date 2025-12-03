import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: 'dashboard', loadChildren: () => import('./dashboard/dashboard-module').then(m => m.DashboardModule) },
  { path: 'ingredients', loadChildren: () => import('./ingredients/ingredients-module').then(m => m.IngredientsModule) },
  { path: 'recipes', loadChildren: () => import('./recipes/recipes-module').then(m => m.RecipesModule) },
  { path: 'food-log', loadChildren: () => import('./food-log/food-log-module').then(m => m.FoodLogModule) },
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' }
];
