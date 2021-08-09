import { Component, Input, OnInit, OnChanges } from '@angular/core';

@Component({
  selector: 'select-list',
  templateUrl: './select-list.component.html',
  styleUrls: ['./select-list.component.scss']
})
export class SelectListComponent implements OnInit, OnChanges{

  @Input() public name: string;
  @Input() public multiple: boolean;
  @Input() public options: Array<any> = new Array<any>();
  @Input() public selectTutor: boolean = false;
  @Input() public preSelect: number;

  public searchValue: string;
  public hiddeDropdown = true;
  public dropdownOptionsOriginal = new Array<string>();
  public dropdownOptions = new Array<string>();
  public selectedItems = new Array<string>();
  public result = new Array<number>();
  public inputValue: string;

  public ngOnInit(): void {
    this.initOptions();
  }

  public ngOnChanges(): void {
    this.initOptions();
  }

  public initOptions(): void {
    this.dropdownOptionsOriginal = new Array<string>();
    this.dropdownOptions = new Array<string>();

    if (this.options && this.options.forEach) {
      this.options.forEach(el => {
        this.dropdownOptionsOriginal.push(el.name);
        this.dropdownOptions.push(el.name);
      });
    }
    if(this.preSelect) {
      let option = this.options.filter(o => o.id == this.preSelect)[0];
      if(option) {
        if(this.multiple) {
          this.addOption(option.name);
        } else {
          this.selectOption(option.name)
        }
      }
    }

  }

  public onChange(): void {
    this.hiddeDropdown = !this.searchValue;
    this.dropdownOptions = this.dropdownOptionsOriginal.filter(o => o.toLocaleLowerCase().indexOf(this.searchValue.toLocaleLowerCase()) > -1)
  }

  public selectOption(option: string): void {
    let op = this.options.filter(o => o.name == option)[0];
    this.searchValue = op.name;
    if(this.selectTutor) {
      this.searchValue+= ' (' + op.tutor + ')';
    }
    this.hiddeDropdown = true;
    this.inputValue = this.options.filter(o => o.name == option)[0].id.toString();
  }

  public addOption(option: string): void {
    this.selectedItems.push(option);
    this.result.push(this.options.filter(o => o.name == option)[0].id);
    this.inputValue = JSON.stringify(this.result);
    this.dropdownOptionsOriginal = this.dropdownOptionsOriginal.filter(o => o != option)
    this.dropdownOptions = this.dropdownOptions.filter(o => o != option);
    this.searchValue = "";
    this.hiddeDropdown = true;
  }

  public deleteItem(item: string): void {
    this.selectedItems = this.selectedItems.filter(i => i != item);
    this.result = this.result.filter(r => r != this.options.filter(o => o.name == item)[0].id);
    this.inputValue = JSON.stringify(this.result);
    this.dropdownOptionsOriginal.push(item);
    this.dropdownOptions.push(item);
  }

}