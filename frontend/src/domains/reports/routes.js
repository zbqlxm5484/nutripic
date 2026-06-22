import * as reports from './pages'

export const reportRoutes = [
  { path: '/reports/generating', component: reports.generatingPage },
  { path: '/reports/new', component: reports.newPage },
  { path: '/reports', component: reports.page },
  { path: '/reports/:report_id', component: reports.detailPage },
]
