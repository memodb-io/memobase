import { ServerError } from './error';
import type { BaseResponse } from './types';

export async function unpackResponse<T>(response: Response): Promise<BaseResponse<T>> {
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = (await response.json()) as BaseResponse<T>;

  if (data.errno !== 0) {
    throw new ServerError(data.errmsg);
  }

  return data;
}
