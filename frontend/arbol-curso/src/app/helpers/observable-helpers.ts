import { Observable } from 'rxjs';
import { filter } from 'rxjs/operators';
import * as _ from 'lodash';



export function filterTrue<T>(obs: Observable<T>) {
  return obs.pipe(filter(_.identity));
}
