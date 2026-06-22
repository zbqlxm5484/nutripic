import * as admin from './pages'

export const adminRoutes = [
  { path: '/admin', component: admin.page },
  { path: '/admin/users', component: admin.usersPage },
  { path: '/admin/posts', component: admin.postsPage },
  { path: '/admin/comments', component: admin.commentsPage },
]
