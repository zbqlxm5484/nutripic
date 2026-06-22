import * as community from './pages'

export const communityRoutes = [
  { path: '/community', component: community.page },
  { path: '/community/new', component: community.newPage },
  { path: '/community/:post_id', component: community.detailPage },
  { path: '/community/:post_id/edit', component: community.editPage },
]
