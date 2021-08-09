import { FormArray } from '@angular/forms';
import * as _ from 'lodash';
import moment from 'moment';



export namespace FormArrayHelpers {
  export function clearFormArray(formArray: FormArray) {
    while (formArray.length !== 0) {
      formArray.removeAt(0);
    }
  }
}


// DFS over values dictionary tree structure. Returns all leaf values keyed by thir path in the dictionary
export function flattenValues(dict: {[key: string]: any}): {[key: string]: any} {
  return _flattenValues(dict, '');
}

function _flattenValues(dict: {[key: string]: any}, prevKey: string) {
  return _.transform(dict, (result, child, childKey) => {
    const key = prevKey + childKey;
    if (_.isPlainObject(child)) {
      _.assign(result, _flattenValues(child, `${key}.`));
    }
    else if (_.isArray(child)) {
      _.transform(child, (result, grandChild, index) => _.assign(result, _flattenValues(grandChild, `${key}[${index}]`)), result)
    }
    else {
      result[key] = child;
    }
  }, {});
}


export function keyPartition(dict: {[key: string]: any}, f: (key: string) => boolean): {[key: string]: any} {
  return _.transform(dict, (result, value, key) => result[f(key) ? 0 : 1][key] = value, [{}, {}]);
}


export function mergeDatetimes(dict: {[key: string]: any}): {[key: string]: any} {
  const mergedDict = {};
  _.forEach(dict, (value, key) => {
    if (key.endsWith('_date')) {
      const m = moment(`${value}T${dict[key.replace(new RegExp('_date$'), '_time')]}:00-03:00`).zone('-03:00');
      mergedDict[key.replace(new RegExp('_date$'), '')] = m.isValid() ? m.format() : null;
    }
    else if (!key.endsWith('_time')) {
      mergedDict[key] = value;
    }
  })
  return mergedDict;
}


export function unmergeDatetimes(dict: {[key: string]: any}): {[key: string]: any} {
  return _.transform(dict, (result, child, childKey) => {
    if (_.isPlainObject(child)) {
      result[childKey] = unmergeDatetimes(child);
    }
    else if (_.isArray(child)) {
      result[childKey] = child.map(e => unmergeDatetimes(e));
    }
    else {
      _unmergeDatetime(child, childKey, result);
    }
  }, {});
}

function _unmergeDatetime(value: any, key: string, dict: {[key: string]: any}) {
  let m = moment(value, moment.ISO_8601, true);
  if (m.isValid()) {
    m = m.zone('-03:00');
    const dateString = m.format();
    dict[`${key}_date`] = dateString.slice(0, 10);
    dict[`${key}_time`] = dateString.slice(11, 16);
  }
  else {
    dict[key] = value;
  }
}
