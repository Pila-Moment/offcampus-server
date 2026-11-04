// Netlify Function: everything under /api/ goes to lib/crews.mjs. Data lives in Netlify Blobs (store "offcampus").
import { getStore } from '@netlify/blobs';
import { handle } from '../../lib/crews.mjs';

export default async (req) => handle(req, getStore({ name: 'offcampus', consistency: 'strong' }));

export const config = { path: '/api/*' };
