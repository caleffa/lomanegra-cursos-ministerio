import { Component, ViewEncapsulation, ViewChild, Input } from '@angular/core';
import { TreeComponent, ITreeOptions, TreeNode } from "angular-tree-component";
import { CoursesAPIService } from './services/api.service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { SegmentComponent } from './components/segment/segment.component';
import { SegmentSectionComponent } from './components/segment-section/segment-section.component';
import { QuestionComponent } from './components/question/question.component';
import { OptionComponent } from './components/option/option.component';
import { SlideComponent } from './components/slide/slide.component';
import { DownloadableDocumentComponent } from './components/downloadable-document/downloadable-document.component';
import { ForumComponent } from './components/forum/forum.component';
import { TareaComponent } from './components/tarea/tarea.component';
import {LiveStreamComponent} from "./components/live-stream/live-stream.component";

// Force rebuild

@Component({
    selector: 'arbol-curso',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss'],
    encapsulation: ViewEncapsulation.None
})
export class AppComponent {
    private addNodeTypes = [
            'SegmentsTitle',
            'LiveStreamsTitle',
            'QuestionnairesTitle',
            'QuestionsTitle',
            'OptionsTitle',
            'SlidesTitle',
            'DocumentsTitle',
            'ForumsTitle',
            'TasksTitle',
        ];
  
    @ViewChild('tree', {static: false}) private tree: TreeComponent;
    @ViewChild('delModal', {static: false}) private delModal;
    @ViewChild('slideDelModal', {static: false}) private slideDelModal;
    @ViewChild('spinnerModal', {static: false}) protected spinnerModal;
    
    @ViewChild('segmentComp', {static: false}) private segmentComp: SegmentComponent;
    @ViewChild('liveStreamComp', {static: false}) private liveStreamComp: LiveStreamComponent;
    @ViewChild('segmentSectionComp', {static: false}) private segmentSectionComp: SegmentSectionComponent;
    @ViewChild('questionComp', {static: false}) private questionComp: QuestionComponent;
    @ViewChild('optionComp', {static: false}) private optionComp: OptionComponent;
    @ViewChild('slideComp', {static: false}) private slideComp: SlideComponent;
    @ViewChild('downloadableDocumentComp', {static: false}) private downloadableDocumentComp: DownloadableDocumentComponent;
    @ViewChild('forumComp', {static: false}) private forumComp: ForumComponent;
    @ViewChild('tareaComp', {static: false}) private tareaComp: TareaComponent;
    
    public options: ITreeOptions = { 
        idField: '_id',
        allowDrag: false,
        allowDrop: false
    };
    private courseId: number;
    public course: any[];
    public delName: string;
    public editingModel: any;
    public editingNode: TreeNode;
    public editingErrors: string[] = [];
    
    private expandeNodes = [];

    @Input('course_id')
    public set _courseId(courseId: number) {
        this.courseId = courseId;
        this.getCourseData();
    }

    public constructor(public apiService: CoursesAPIService,
        private modalService: NgbModal) {
    }

    public expandTree() {
        this.tree.treeModel.expandAll();
    }

    public collapseTree() {
        this.tree.treeModel.expandedNodeIds = { }; 
    }

    public getCourseData(): void {
        if(this.tree) {
            this.expandeNodes = [];
            this.tree.treeModel.nodes.forEach(node => { this.saveNodeState(node) });
        }
        this.apiService.get('course', this.courseId).subscribe(course => {
            let cour = [course.children[0], course.children[1]];
            this.addCustomIds(cour[0], cour[0].id);
            this.addCustomIds(cour[1], cour[1].id);
            this.course = cour;
            if(this.tree.treeModel.nodes) {
                this.tree.treeModel.nodes.forEach(node => { this.applyNodeState(node) });
            }
        });
    }

    private addCustomIds(item: any, parentId: number): void {
        // Usamos un ID custom en los nodos del árbol porque como provienen de distintos modelos en el backend
        // y todos usan ID numérico, si solo usamos el ID de la base de datos, vamos a tener nodos de distintos
        // modelos cuyos IDs coinciden, y necesitamos que sean únicos en el árbol. Entonces para referenciarlos
        // en el árbol, usamos el campo _id que está compuesto por el tipo + el ID de la base.
        let _id;
        if(item.id && item.type) {
            _id = item.type + '_' + item.id.toString();
        } else if (item.name) {
            _id = item.name + '_' + parentId.toString();
        }
        item._id = _id;
        if(item.children) {
            item.children.forEach(i => { this.addCustomIds(i, item.id) });
        }
    }

    private saveNodeState(node: TreeNode) {
        if(node.isExpanded) {
            this.expandeNodes.push(node['_id']);
            node.children.forEach(n => { this.saveNodeState(n) });
        }
    }

    private applyNodeState(node: TreeNode): void {
        if(this.expandeNodes.indexOf(node['_id']) > -1) {
            node.expand();
            node.children.forEach(n => { this.applyNodeState(n) });
        }
    }

    private getComponent(node: TreeNode) {
        if(node.data.type == 'SegmentsTitle' || node.data.type == 'Segment') {
            return this.segmentComp;
        } else if(node.data.type == 'LiveStreamsTitle' || node.data.type == 'LiveStream') {
            return this.liveStreamComp;
        } else if(node.data.type == 'QuestionnairesTitle' || node.data.type == 'SegmentSection') {
            return this.segmentSectionComp;
        } else if(node.data.type == 'QuestionsTitle' || node.data.type == 'Question') {
            return this.questionComp;
        } else if(node.data.type == 'OptionsTitle' || node.data.type == 'Option') {
            return this.optionComp;
        } else if(node.data.type == 'SlidesTitle' || node.data.type == 'Slide') {
            return this.slideComp;
        } else if (node.data.type == 'DocumentsTitle' || node.data.type == 'DownloadableDocument') {
            return this.downloadableDocumentComp;
        } else if (node.data.type == 'ForumsTitle' || node.data.type == 'Forum') {
            return this.forumComp;
        } else if (node.data.type == 'TasksTitle' || node.data.type == 'Tarea') {
            return this.tareaComp;
        }
    }

    public add(node: TreeNode) {
        let component = this.getComponent(node);
        if(node.data.id) {
            component.add(node.data.id);
        } else {
            component.add(node.parent.data.id);
        }
    }

    public edit(node: TreeNode) {
        let component = this.getComponent(node);
        console.log('node ', node);
        let parentId;
        if (node.data.type === 'Segment') {
            parentId = node.parent.data.id;
        } else if (node.data.type === 'SegmentSection') {
            parentId = node.parent.parent.data.id;
        }
        component.load(node.data.id, parentId);
    }

    public delete(node: TreeNode) {
        this.delName = node.data.name;
        this.modalService.open(this.delModal).result.then(d => {
            if(node.data.type == 'Slide' && node.parent.children.length == 1) {
                this.modalService.open(this.slideDelModal);
            } else {
                let component = this.getComponent(node);
                component.delete(node.data.id);
            }
        }, c=>{});
    }

    public isAddNode(node) {
        return (this.addNodeTypes.indexOf(node.data.type) !== -1) || !node.data.type
    }

    public isDeleteNode(node) {
        return (this.addNodeTypes.indexOf(node.data.type) === -1) && !!node.data.type;
    }

    public isEditNode(node) {
        return this.isDeleteNode(node);
    }

}
